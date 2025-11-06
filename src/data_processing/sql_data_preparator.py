import json
import sqlite3
import time
from openai import OpenAI

from src.config.config import Config
from src.data_processing.data_processing_utils import DataProcessingUtils


class SqlDataPreparator:
    """Class for preparing database and metadata files."""

    def __init__(self, client: OpenAI, config: Config):
        """
        Initialize DataPreparator.

        Args:
            client: OpenAI client instance
            config: Application configuration including models and paths
        """
        self.client = client
        self.config = config
        self.gpt_model = config.model_prepare_data

        # Setup paths
        self.db_zip_path = self.config.folder_data / "northwind.zip"
        self.db_metadata_format_path = self.config.folder_data / "metadata_format.json"

        self.db_file_path = self.config.folder_ready / "northwind.db"
        self.db_schema_path = self.config.folder_ready / "northwind_schema.sql"

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
            with open(self.config.file_sql_metadata, 'w', encoding='utf-8') as f:
                f.write(metadata)

            # End timing
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.gpt_model.prepare_statistics(elapsed_time, response.usage).print()

        except Exception as e:
            print(f"Error generating metadata: {str(e)}")
            raise

    def prepare_sql_data(self):
        """
        Prepare SQL database data: unzip, extract schema, generate metadata.
        This is the main method that orchestrates all preparation steps.
        """

        DataProcessingUtils.unzip_file(self.db_zip_path, self.config.folder_ready)
        self.extract_schema()
        self.generate_metadata()

        print("DATABASE PREPARATION COMPLETE")
