import json
import re
import time
from openai import OpenAI
from src.config.config import Config
from src.data_processing.data_processing_utils import DataProcessingUtils
from src.models.gpt_model import ApiStatistics


class TextDataPreparator:
    """
    A class to prepare text data from the MAVEN dataset.
    Handles unzipping and processing of JSONL files.
    """

    def __init__(self, client: OpenAI, config: Config):
        """
        Initialize the TextDataPreparator.

        Args:
            config: Application configuration including models and paths
            client: OpenAI client instance for generating embeddings
        """
        self.client = client
        self.config = config
        self.model = config.model_embeddings
        self.zip_path = config.folder_data / "MAVEN-dataset.zip"
        self.extract_dir = config.folder_data
        self.jsonl_path = self.extract_dir / 'test.jsonl'
        self.file_articles_raw = config.folder_ready / 'articles_raw.json'
        self.processed_documents = []

    def process_jsonl(self):
        """
        Process JSONL file by reading each line, extracting sentences
        from the 'content' array, and concatenating them with spaces.
        """
        print(f"Processing {self.jsonl_path}...")

        with open(self.jsonl_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue

                try:
                    doc = json.loads(line)

                    sentences = []
                    for item in doc['content']:
                        sentences.append(item['sentence'])

                    concatenated_text = ' '.join(sentences)
                    self.processed_documents.append({"id": doc['id'], "title": doc['title'], "text": concatenated_text, "length": len(concatenated_text)})

                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON on line {line_num}: {e}")
                    continue

            print(f"Total documents processed: {len(self.processed_documents)}")

        # Save articles for easy review
        with open(self.file_articles_raw, 'w', encoding='utf-8') as f:
            json.dump(self.processed_documents, f, ensure_ascii=False, indent=2)

        # Clean up extracted JSONL file
        self.jsonl_path.unlink()

    def chunk_text_by_sentence(self, text: str, chunk_size: int = 512, overlap_sentences: int = 1) -> list[str]:
        """
        Split text into chunks by sentences with sentence-level overlap

        Args:
            text: Input text to chunk
            chunk_size: Maximum size of each chunk in characters
            overlap_sentences: Number of sentences to overlap between chunks (default: 1)
        """

        # Split text into sentences using regex
        sentence_pattern = r'[^.!?]+[.!?]+|[^.!?]+$'
        sentences = [s.strip() for s in re.findall(sentence_pattern, text) if s.strip()]

        if not sentences:
            return [text] if text.strip() else []

        chunks = []
        i = 0

        while i < len(sentences):
            chunk_sentences = []
            chunk_length = 0

            # Add sentences until we reach chunk_size
            j = i
            while j < len(sentences):
                sentence = sentences[j]
                sentence_length = len(sentence) + 1  # +1 for space

                # If chunk_size is exceeded already, it is not a problem if adding this one might exceed chunk_length
                if chunk_length > chunk_size:
                    break

                chunk_sentences.append(sentence)
                chunk_length += sentence_length
                j += 1

            # Create the chunk from collected sentences if it does not contain overlap sentences from previous chunk
            if not (chunks and len(chunk_sentences) <= overlap_sentences):
                chunks.append(' '.join(chunk_sentences))

            # Move to next chunk position with overlap
            # Move forward by the number of sentences minus overlap
            sentences_to_advance = max(1, len(chunk_sentences) - overlap_sentences)
            i += sentences_to_advance

        return chunks

    def chunk_text_by_length(self, text, chunk_size: int = 512, overlap: int = 50):
        """
        Split text into chunks of specified word count with overlap.

        Args:
            text: The text to chunk
            chunk_size: Number of words per chunk (default: 512)
            overlap: Number of words to overlap between chunks (default: 50)

        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)

            if i + chunk_size >= len(words):
                break

        return chunks

    def generate_embeddings_for_chunks(self, chunk_by_sentence: bool):
        """
        Process articles by chunking them and generating embeddings for each chunk.
        Saves the results with embeddings to a JSON file.
        """

        if chunk_by_sentence:
            print(f"Processing articles for chunking by sentence and embedding generation...")
        else:
            print(f"Processing articles for chunking by length and embedding generation...")

        chunked_documents = []
        chunk_id = 0
        statistics: ApiStatistics = None
        for _, article in enumerate(self.processed_documents):
            if chunk_by_sentence:
                chunks = self.chunk_text_by_sentence(article['text'])
            else:
                chunks = self.chunk_text_by_length(article['text'])

            # Generate embeddings for each chunk
            for chunk_idx, chunk in enumerate(chunks):
                try:
                    # Start timing
                    start_time = time.time()

                    response = self.client.embeddings.create(input=chunk, model=self.model.model_name)

                    embedding = response.data[0].embedding

                    # End timing
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    statistics = self.model.prepare_statistics(elapsed_time, response.usage).sum(statistics)

                    # Create chunk document with embedding
                    chunk_doc = {
                        'chunk_id': chunk_id,
                        'article_id': article['id'],
                        'article_title': article['title'],
                        'chunk_index': chunk_idx,
                        'text': chunk,
                        'embedding': embedding
                    }

                    chunked_documents.append(chunk_doc)
                    chunk_id += 1

                    # Print progress every 100 chunks
                    if chunk_id % 100 == 0:
                        print(f"Processed {chunk_id} chunks...")
                        statistics.print()

                except Exception as e:
                    print(f"  Error generating embedding for chunk {chunk_idx}: {str(e)}")
                    continue

        try:
            if chunk_by_sentence:
                output_file = self.config.file_articles_sentences
            else:
                output_file = self.config.file_articles_length

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(chunked_documents, f, ensure_ascii=False, indent=2)

            print(f"Successfully saved {len(chunked_documents)} chunks with embeddings to {output_file}")
            statistics.print()

        except Exception as e:
            print(f"Error saving embeddings: {str(e)}")
            raise

    def prepare_articles(self):
        """
        Prepare articles data: unzip, process JSONL, save to CSV.
        This is the main method that orchestrates all preparation steps.
        """
        DataProcessingUtils.unzip_file(self.zip_path, self.extract_dir)
        self.process_jsonl()
        if not self.config.file_articles_sentences.exists():
            self.generate_embeddings_for_chunks(chunk_by_sentence=True)
        if not self.config.file_articles_length.exists():
            self.generate_embeddings_for_chunks(chunk_by_sentence=False)

        print("ARTICLES PREPARATION COMPLETE")
