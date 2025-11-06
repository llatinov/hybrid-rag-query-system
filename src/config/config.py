from pathlib import Path
from src.models.gpt_model import GPTModel


class Config:
    """Configuration for the application including models, paths, and settings."""

    def __init__(
        self,
        open_ai_api_key: str,
        model_prepare_data: str,
        model_sql_assistant: str,
        model_text_assistant: str,
        model_answer_generator: str,
        model_embeddings: str,
        folder_data: str,
        folder_ready: str,
        file_sql_metadata: str,
        file_db: str,
        file_articles_sentences: str,
        file_articles_length: str,
        file_articles_raw: str,
        sql_search_debug: bool,
        text_search_debug: bool
    ):
        """
        Initialize the configuration.

        Args:
            open_ai_api_key: OpenAI API key
            model_prepare_data: Model name for data preparation
            model_sql_assistant: Model name for SQL query analysis
            model_text_assistant: Model name for text query analysis
            model_answer_generator: Model name for answer generation
            model_embeddings: Model name for text embeddings
            folder_data: Path to data folder
            folder_ready: Path to ready content folder
            file_sql_metadata: Path to SQL metadata file
            file_db: Path to database file
            file_articles_sentences: Path to file with articles and embeddings that are chunked by sentences
            file_articles_length: Path to file with articles and embeddings that are chunked by length
            file_articles_raw: Path to file with full articles content
            sql_search_debug: Whether to show detailed SQL analysis
            text_search_debug: Whether to show detailed text search analysis
        """
        self.open_ai_api_key = open_ai_api_key

        # Convert model names to GPTModel instances
        self.model_prepare_data = GPTModel(model_name=model_prepare_data)
        self.model_sql_assistant = GPTModel(model_name=model_sql_assistant)
        self.model_text_assistant = GPTModel(model_name=model_text_assistant)
        self.model_answer_generator = GPTModel(model_name=model_answer_generator)
        self.model_embeddings = GPTModel(model_name=model_embeddings)

        # Set up paths
        self.folder_data = folder_data
        self.folder_ready = folder_ready
        self.file_sql_metadata = file_sql_metadata
        self.file_db = file_db
        self.file_articles_sentences = file_articles_sentences
        self.file_articles_length = file_articles_length
        self.file_articles_raw = file_articles_raw

        self.sql_search_debug = sql_search_debug
        self.text_search_debug = text_search_debug
