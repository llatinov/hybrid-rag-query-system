import zipfile
from pathlib import Path


class DataProcessingUtils:
    """Utility functions for data processing operations."""

    @staticmethod
    def unzip_file(zip_path: Path, extract_dir: Path):
        """
        Unzip a file to the specified directory.

        Args:
            zip_path: Path to the ZIP file
            extract_dir: Directory to extract files to

        Raises:
            Exception: If extraction fails
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            print(f"Successfully extracted files from {zip_path.name}")
        except Exception as e:
            print(f"Error during extraction of '{zip_path}': {str(e)}")
            raise
