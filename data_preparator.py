import json
import os
import sqlite3
import sys
import time
import zipfile
from openai import OpenAI
from os import path
from pathlib import Path

from gpt_model import GPTModel


class DataPreparator:
    """Class for preparing database and metadata files."""

    def __init__(self, client: OpenAI, gpt_model: GPTModel):
        """
        Initialize DataPreparator.

        Args:
            client: OpenAI client instance
            gpt_model: GPTModel instance for API calls
        """
        self.client = client
        self.gpt_model = gpt_model

        # Setup paths
        self.data_folder = Path(__file__).parent / "data"
        self.ready_folder = self.data_folder / "ready"

        self.db_zip_path = self.data_folder / "northwind.zip"
        self.db_metadata_format_path = self.data_folder / "metadata_format.json"

        self.db_file_path = self.ready_folder / "northwind.db"
        self.db_schema_path = self.ready_folder / "northwind_schema.sql"
        self.db_metadata_path = self.ready_folder / "northwind_schema.json"
        self.db_metadata_tables_path = self.ready_folder / "northwind_schema_tables.json"

    def unzip_database(self):
        """Unzip the database ZIP file in the current directory."""
        print(f"Unzipping {self.db_zip_path}...")
        print(f"Extracting to: {self.ready_folder}")

        try:
            with zipfile.ZipFile(self.db_zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.ready_folder)
            print(f"Successfully extracted database")
        except Exception as e:
            print(f"Error during extraction: {str(e)}")
            raise

    def extract_schema(self):
        """Extract the full schema and save to a file."""
        print(f"Connecting to {self.db_file_path}...")

        try:
            # Connect to the database
            conn = sqlite3.connect(self.db_file_path)
            cursor = conn.cursor()

            # Get the full schema (equivalent to .fullschema command)
            # This retrieves all CREATE statements for tables, indexes, triggers, and views
            cursor.execute("""
                SELECT sql || ';'
                FROM sqlite_master
                WHERE sql IS NOT NULL
                ORDER BY type DESC, name
            """)

            schema_statements = cursor.fetchall()

            # Write schema to file
            with open(self.db_schema_path, 'w', encoding='utf-8') as f:
                f.write(f"-- {self.db_file_path} Database Full Schema\n")

                for statement in schema_statements:
                    f.write(statement[0] + '\n\n')

            conn.close()

            print(f"Successfully extracted schema to {self.db_schema_path}")
            print(f"Found {len(schema_statements)} schema objects")

        except Exception as e:
            print(f"Error extracting schema: {str(e)}")
            raise

    def generate_metadata(self):
        """Generate database metadata description using OpenAI API."""
        print(f"Reading schema from {self.db_schema_path}...")

        try:
            # Start timing
            start_time = time.time()

            # Read the schema SQL file
            with open(self.db_schema_path, 'r', encoding='utf-8') as f:
                schema_content = f.read()

            # Read the metadata output format
            with open(self.db_metadata_format_path, 'r', encoding='utf-8') as f:
                response_format_schema = json.loads(f.read())

            print("Generating metadata using OpenAI API...")

            # Call OpenAI API to generate metadata
            response = self.client.chat.completions.create(
                model=self.gpt_model.model_name,
                reasoning_effort="high",
                response_format={
                    "type": "json_schema",
                    "json_schema": response_format_schema
                },
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a database documentation expert. Analyze SQL schemas and provide clear, comprehensive descriptions.
                         The descriptions should be in format understandable by large language models.
                         The descriptions will be used by LLM to map user input to a database table."""
                    },
                    {
                        "role": "user",
                        "content": f"""Analyze the following database schema and provide a comprehensive description including:

1. Database Overview: Brief description of the database purpose
2. Tables: List all tables with their purpose and key columns
3. Relationships: Describe foreign key relationships and how tables relate to each other
4. Indexes: Note any indexes and their purpose
5. Data Model Summary: Overall data model architecture

A table in described from following records:
1. CREATE VIEW []
2. CREATE TABLE []

Please format the output in the provided JSON structure.

Schema:
```sql
{schema_content}
```"""
                    }
                ],
            )

            metadata = response.choices[0].message.content

            # Save metadata to file
            with open(self.db_metadata_path, 'w', encoding='utf-8') as f:
                f.write(metadata)

            # End timing
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Calculate cost

            print(f"Successfully generated metadata to {self.db_metadata_path}")
            print(f"API call took {elapsed_time:.2f} seconds")
            self.gpt_model.print_cost(response.usage)

        except Exception as e:
            print(f"Error generating metadata: {str(e)}")
            raise

    def prepare_sql_data(self):
        """
        Prepare SQL database data: unzip, extract schema, generate metadata.
        This is the main method that orchestrates all preparation steps.
        """
        print("\n" + "="*80)
        print("DATABASE PREPARATION")
        print("="*80)
        print()

        # Step 1: Unzip database
        if not self.db_file_path.exists():
            self.unzip_database()
        else:
            print("✓ Database file already exists")

        # Step 2: Extract schema
        if not self.db_schema_path.exists():
            self.extract_schema()
        else:
            print("✓ Schema file already exists")

        # Step 3: Generate metadata
        if not self.db_metadata_path.exists():
            self.generate_metadata()
        else:
            print("✓ Metadata file already exists")

        print("\n" + "="*80)
        print("DATABASE PREPARATION COMPLETE")
        print("="*80)
