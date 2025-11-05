from pathlib import Path
from src.models.gpt_model import GPTModel


class Config:
    """Configuration for the application including models, paths, and settings."""

    def __init__(
        self,
        open_ai_api_key: str,
        model_prepare_data: str,
        model_sql_assistant: str,
        model_answer_generator: str,
        folder_data: str,
        folder_db: str,
        file_sql_metadata: str,
        file_db: str,
        sql_debug: bool
    ):
        """
        Initialize the configuration.

        Args:
            open_ai_api_key: OpenAI API key
            model_prepare_data: Model name for data preparation
            model_sql_assistant: Model name for SQL query analysis
            model_answer_generator: Model name for answer generation
            folder_data: Path to data folder
            folder_db: Path to database folder
            file_sql_metadata: Path to SQL metadata file
            file_db: Path to database file
            sql_debug: Whether to show detailed SQL analysis
        """
        self.open_ai_api_key = open_ai_api_key

        # Convert model names to GPTModel instances
        self.model_sql_assistant = GPTModel(model_name=model_sql_assistant)
        self.model_prepare_data = GPTModel(model_name=model_prepare_data)
        self.model_answer_generator = GPTModel(model_name=model_answer_generator)

        # Set up paths
        self.folder_data = folder_data
        self.folder_db = folder_db
        self.file_sql_metadata = file_sql_metadata
        self.file_db = file_db

        self.sql_debug = sql_debug
