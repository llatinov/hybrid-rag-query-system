import json
import sqlite3
import time
from openai import OpenAI
from pathlib import Path
from gpt_model import GPTModel


class SQLQueryAssistant:
    """Assistant for analyzing user questions and generating SQL queries."""

    def __init__(self, client: OpenAI, metadata_path: Path, gpt_model: GPTModel, db_path: Path):
        """
            Initialize the SQL Query Assistant.

            Args:
                client: OpenAI client instance
                metadata_path: Path to the database metadata JSON file
                gpt_model: GPTModel instance with model configuration
                db_path: Path to the SQLite database file
            """
        self.client = client
        self.metadata = self._load_metadata(metadata_path)
        self.gpt_model = gpt_model
        self.db_path = db_path

    def _load_metadata(self, metadata_path: Path) -> dict:
        """Load the database metadata from JSON file."""
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Metadata file not found at {metadata_path}")
            raise
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON metadata: {e}")
            raise

    def execute_query(self, sql_query: str) -> dict:
        """
        Execute a SQL query against the database.

        Args:
            sql_query: SQL query to execute

        Returns:
            Dictionary with:
            - success: bool indicating if query succeeded
            - columns: list of column names (if success)
            - rows: list of result rows (if success)
            - row_count: number of rows returned (if success)
            - error: error message (if failed)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(sql_query)

            # Get column names from cursor description
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            # Fetch all results
            rows = cursor.fetchall()
            row_count = len(rows)

            conn.close()

            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": row_count
            }

        except sqlite3.Error as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    def analyze_question(self, question: str) -> tuple:
        """
        Send question to OpenAI to analyze and break down into SQL subtasks.

        Args:
            question: User's natural language question

        Returns a dictionary with:
        - explanation: Natural language explanation of the question
        - relevant_tables: List of tables needed to answer the question
        - subtasks: List of subtasks with SQL queries
        """

        # Format metadata for the prompt
        metadata_str = json.dumps(self.metadata, indent=2)

        prompt = f"""You are a database query assistant. Given a user's question and database metadata, your task is to:

1. Explain what the user is asking for in clear terms
2. Identify which database tables are relevant to answer this question
3. Break down the question into logical subtasks
4. For each subtask, provide a SQL query that can be executed

Database Metadata:
```json
{metadata_str}
```

Support only data retrieval operations, in case of data insert of modification request:
1. Return that "only select operations are supported"
2. Break and do not produce any subtasks

User Question: {question}

Please provide your response in the following JSON format:
{{
  "explanation": "Clear explanation of what the user is asking",
  "relevant_tables": ["table1", "table2", ...],
  "subtasks": [
    {{
      "description": "What this subtask accomplishes",
      "sql_query": "SELECT ... FROM ...",
      "rationale": "Why this query is needed"
    }}
  ]
}}
"""

        try:
            # Start timing
            start_time = time.time()

            response = self.client.chat.completions.create(
                model=self.gpt_model.model_name,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SQL database assistant. You analyze user questions and break them down into executable SQL queries. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )

            # End timing
            end_time = time.time()
            elapsed_time = end_time - start_time

            result = json.loads(response.choices[0].message.content)
            statistics = self.gpt_model.prepare_statistics(elapsed_time, response.usage)
            return result, statistics

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None, None

    def process_analysis(self, analysis: dict) -> tuple:
        """
        Display the analysis results in a formatted way.

        Args:
            analysis: Analysis dictionary from analyze_question
        """
        console_output = []
        gpt_input = []

        console_output.append("\n📝 Explanation:")
        console_output.append(f"   {analysis['explanation']}")
        console_output.append("\n📊 Relevant Tables:")

        for table in analysis['relevant_tables']:
            console_output.append(f"   - {table}")

        console_output.append("\n🔍 Query Breakdown:")
        gpt_input = console_output.copy()

        for i, subtask in enumerate(analysis['subtasks'], 1):
            subtask_output = []
            subtask_output.append(f"\n   Subtask {i}: {subtask['description']}")
            subtask_output.append(f"   Rationale: {subtask['rationale']}")
            subtask_output.append(f"   SQL Query: {subtask['sql_query']}")

            result = self.execute_query(subtask['sql_query'])
            if result['success']:
                if result['row_count'] > 0:
                    # Display column headers
                    subtask_output.append("\n   Results:")
                    subtask_output.append("   " + " | ".join(result['columns']))
                    subtask_output.append("   " + "-" * 60)

                    # Display rows (limit to first 10 for readability)
                    max_rows = 10
                    for _, row in enumerate(result['rows'][:max_rows]):
                        row_str = " | ".join(str(val) if val is not None else "NULL" for val in row)
                        subtask_output.append(f"   {row_str}")

                    if result['row_count'] > max_rows:
                        subtask_output.append(f"   ... ({result['row_count'] - max_rows} more rows)")

                    # Add to GPT prompt only if successful
                    gpt_input.extend(subtask_output)
                else:
                    subtask_output.append("   No rows returned.")
            else:
                subtask_output.append(f"   ❌ Query failed: {result['error']}")
            console_output.extend(subtask_output)

        return console_output, gpt_input
