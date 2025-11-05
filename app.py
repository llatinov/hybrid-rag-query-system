import os
from pathlib import Path
from src.assistants.query_assistant import QueryAssistant
from src.config.config import Config


def main():
    """Main entry point for the application."""

    folder_data = Path(__file__).parent / "data"
    folder_db = folder_data / "db"
    # Configure the application
    config = Config(
        open_ai_api_key=os.getenv('OPENAI_API_KEY'),
        model_prepare_data="gpt-5",
        model_sql_assistant="gpt-5-mini",
        model_answer_generator="gpt-5-mini",
        folder_data=folder_data,
        folder_db=folder_db,
        file_sql_metadata=folder_db / "northwind_schema.json",
        file_db=folder_db / "northwind.db",
        sql_debug=os.getenv('SQL_DEBUG', 'true').lower() in ('true', '1', 'yes'),
    )

    try:
        # Initialize and run the query assistant
        assistant = QueryAssistant(config=config)
        assistant.run()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
