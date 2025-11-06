import os
from pathlib import Path
from src.assistants.query_assistant import QueryAssistant
from src.config.config import Config


def main():
    """Main entry point for the application."""

    folder_data = Path(__file__).parent / "data"
    folder_ready = folder_data / "ready"
    # Configure the application
    config = Config(
        open_ai_api_key=os.getenv('OPENAI_API_KEY'),
        model_prepare_data="gpt-5",
        model_sql_assistant="gpt-5-mini",
        model_answer_generator="gpt-5-mini",
        model_embeddings="text-embedding-3-small",
        folder_data=folder_data,
        folder_ready=folder_ready,
        file_sql_metadata=folder_ready / "northwind_schema.json",
        file_db=folder_ready / "northwind.db",
        file_articles_sentences=folder_ready / "articles_by_sentence_with_embeddings.json",
        file_articles_length=folder_ready / "articles_by_length_with_embeddings.json",
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
