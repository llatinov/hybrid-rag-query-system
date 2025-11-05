import json
import os
import sqlite3
import time
import zipfile
from openai import OpenAI
from os import path
from pathlib import Path


def unzip_database(zip_file: str):
    """Unzip the database ZIP file in the current directory."""
    # Get the directory where this script is located
    zip_path = CURRENT_FOLDER / zip_file
    extract_to = READY_FOLDER / "."

    print(f"Unzipping {zip_path}...")
    print(f"Extracting to: {extract_to}")

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Successfully extracted {zip_file}")
    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        raise e


def extract_schema(db_path: str, schema_output_path: str):
    """Extract the full schema and save to a file."""
    print(f"Connecting to {db_path}...")

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
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
        with open(schema_output_path, 'w', encoding='utf-8') as f:
            f.write(f"-- {db_path} Database Full Schema\n")

            for statement in schema_statements:
                f.write(statement[0] + '\n\n')

        conn.close()

        print(f"Successfully extracted schema to {schema_output_path}")
        print(f"Found {len(schema_statements)} schema objects")

    except Exception as e:
        print(f"Error extracting schema: {str(e)}")
        raise e


def generate_metadata(db_schema_path: str, db_metadata_path: str, metadata_format_path: str):
    """Generate database metadata description using OpenAI API."""
    print(f"Reading schema from {db_schema_path}...")

    try:
        # Start timing
        start_time = time.time()

        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print(
                "OPENAI_API_KEY environment variable is not set. "
                "Please generate one at: https://platform.openai.com/docs/quickstart "
                "and set it with: export OPENAI_API_KEY='your_api_key_here'"
            )
            return

        client = OpenAI(api_key=api_key)

        # Read the schema SQL file
        with open(db_schema_path, 'r', encoding='utf-8') as f:
            schema_content = f.read()

        # Read the metadata output format
        with open(metadata_format_path, 'r', encoding='utf-8') as f:
            response_format_schema = json.loads(f.read())

        print("Generating metadata using OpenAI API...")

        # Call OpenAI API to generate metadata
        response = client.chat.completions.create(
            model="gpt-5",  # most sophisticated reasoning model
            reasoning_effort="high",  # depth of reasoning for reasoning
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
        with open(db_metadata_path, 'w', encoding='utf-8') as f:
            f.write(metadata)

        # End timing
        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"Successfully generated metadata to {db_metadata_path}")
        print(f"API call took {elapsed_time:.2f} seconds")
        print(f"Usage statistics: {response.usage}")

    except Exception as e:
        print(f"Error generating metadata: {str(e)}")
        raise e


def extract_tables_metadata(db_metadata_path: str, tables_metadata_path: str):
    """Create a simplified version of metadata without columns and indexes."""
    print(f"Reading metadata from {db_metadata_path}...")

    try:
        # Read the full metadata
        with open(db_metadata_path, 'r', encoding='utf-8') as f:
            full_metadata = json.load(f)

        # Create simplified structure
        simplified = {
            "database_name": full_metadata.get("database_name", ""),
            "description": full_metadata.get("description", ""),
            "tables": []
        }

        # Iterate over tables and keep only name, type, description, and relationships
        for table in full_metadata.get("tables", []):
            simple_table = {
                "type": table.get("type", "table"),
                "name": table.get("name", ""),
                "description": table.get("description", "")
            }

            # Only include relationships if they exist and this a table (not a view)
            if "relationships" in table and table["relationships"] and simple_table["type"] == "table":
                simple_table["relationships"] = table["relationships"]

            simplified["tables"].append(simple_table)

        # Save simplified metadata
        with open(tables_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(simplified, f, indent=2)

        print(f"Successfully created simplified metadata at {tables_metadata_path}")
        print(f"Simplified {len(simplified['tables'])} tables")

    except Exception as e:
        print(f"Error simplifying metadata: {str(e)}")
        raise e


if __name__ == "__main__":
    CURRENT_FOLDER = Path(__file__).parent
    READY_FOLDER = CURRENT_FOLDER / "ready"

    DB_ZIP_PATH = CURRENT_FOLDER / "northwind.zip"
    DB_METADATA_FORMAT_PATH = CURRENT_FOLDER / "metadata_format.json"

    DB_FILE_PATH = READY_FOLDER / "northwind.db"
    DB_SCHEMA_PATH = READY_FOLDER / "northwind_schema.sql"
    DB_METADATA_PATH = READY_FOLDER / "northwind_schema.json"
    DB_METADATA_TABLES_PATH = READY_FOLDER / "northwind_schema_tables.json"

    unzip_database(DB_ZIP_PATH)
    extract_schema(DB_FILE_PATH, DB_SCHEMA_PATH)
    if not path.exists(DB_METADATA_PATH):
        generate_metadata(DB_SCHEMA_PATH, DB_METADATA_PATH, DB_METADATA_FORMAT_PATH)
    elif not path.exists(DB_METADATA_TABLES_PATH):
        extract_tables_metadata(DB_METADATA_PATH, DB_METADATA_TABLES_PATH)
