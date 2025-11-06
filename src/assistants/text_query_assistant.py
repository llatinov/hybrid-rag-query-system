import json
import time
import numpy as np
from openai import OpenAI
from src.config.config import Config
from src.models.gpt_model import ApiStatistics


class TextQueryAssistant:
    """Assistant for querying articles using semantic search and keyword matching."""

    def __init__(self, client: OpenAI, config: Config, use_sentence_chunks: bool = True):
        """
        Initialize the TextQueryAssistant.

        Args:
            client: OpenAI client instance
            config: Application configuration
            use_sentence_chunks: Whether to use sentence-based or length-based chunks
        """
        self.client = client
        self.config = config
        self.use_sentence_chunks = use_sentence_chunks
        self.articles_with_embeddings = []
        self.articles_raw = []

        # Load articles with embeddings
        self._load_articles()

    def _load_articles(self):
        """Load articles with embeddings from JSON file."""
        if self.use_sentence_chunks:
            file_path = self.config.file_articles_sentences
        else:
            file_path = self.config.file_articles_length

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.articles_with_embeddings = json.load(f)
            print(f"Loaded {len(self.articles_with_embeddings)} article chunks")
        except Exception as e:
            raise RuntimeError(f"Error loading articles: {e}")

        try:
            with open(self.config.file_articles_raw, 'r', encoding='utf-8') as f:
                self.articles_raw = json.load(f)
            print(f"Loaded {len(self.articles_raw)} full articles")
        except Exception as e:
            raise RuntimeError(f"Error loading articles: {e}")

    def expand_query(self, query: str) -> tuple[list[str], list[str], ApiStatistics]:
        """
        Generate similar query versions and extract keywords using OpenAI.

        Args:
            query: Original user query

        Returns:
            Tuple of (query_versions: list[str], keywords: list[str], statistics: ApiStatistics)
        """
        prompt = f"""Given the user query below, generate 3 similar search queries that maintain the same meaning but use different wording, sampled from the full distribution. Also extract 3-5 important keywords for text search which are not common widely used words.

User Query: "{query}"

Respond in JSON format:
{{
  "query_versions": ["version1", "version2", "version3"],
  "keywords": ["keyword1", "keyword2", "keyword3", ...]
}}"""

        try:
            # Start timing
            start_time = time.time()

            response = self.client.chat.completions.create(
                model=self.config.model_text_assistant.model_name,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates query variations and extracts keywords for semantic search."
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

            # Parse response
            result = json.loads(response.choices[0].message.content)
            query_versions = result.get("query_versions", [query])
            keywords = result.get("keywords", [])

            # Add original query to versions
            all_queries = [query] + query_versions

            # Calculate statistics
            statistics = self.config.model_text_assistant.prepare_statistics(elapsed_time, response.usage)

            return all_queries, keywords, statistics

        except Exception as e:
            print(f"Error expanding query: {e}")
            return [query], [], ApiStatistics.empty()

    def generate_query_embedding(self, query: str) -> np.ndarray:
        """
        Generate embedding for a query.

        Args:
            query: Query text

        Returns:
            Numpy array of embedding vector
        """
        try:
            response = self.client.embeddings.create(
                input=query,
                model=self.config.model_embeddings.model_name
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return None

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score (0 to 1)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2)

    def semantic_search(self, query_versions: list[str], top_k: int = 10) -> list[dict]:
        """
        Search articles using semantic similarity with multiple query versions.

        Args:
            query_versions: List of query variations
            top_k: Number of top results to return

        Returns:
            List of article chunks with similarity scores
        """
        # Generate embeddings for all query versions
        query_embeddings = []
        for query in query_versions:
            embedding = self.generate_query_embedding(query)
            if embedding is not None:
                query_embeddings.append(embedding)

        if not query_embeddings:
            return []

        # Calculate similarity scores for each article
        results = []
        for article in self.articles_with_embeddings:
            article_embedding = np.array(article['embedding'])

            # Calculate max similarity across all query versions
            max_similarity = 0
            for query_embedding in query_embeddings:
                similarity = self.cosine_similarity(query_embedding, article_embedding)
                max_similarity = max(max_similarity, similarity)

            results.append({
                'id': article['article_id'],
                'title': article['article_title'],
                'text': article['text'],
                'similarity': max_similarity
            })

        # Sort by similarity and return top_k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]

    def keyword_search(self, keywords: list[str], top_k: int = 10) -> list[dict]:
        """
        Search articles using keyword matching (full-text search).

        Args:
            keywords: List of keywords to search for
            top_k: Number of top results to return

        Returns:
            List of article chunks with match counts
        """
        if not keywords:
            return []

        results = []
        for article in self.articles_raw:
            text_lower = article['text'].lower()

            # Count keyword matches
            match_count = 0
            matched_keywords = []
            for keyword in keywords:
                keyword_lower = keyword.lower()
                count = text_lower.count(keyword_lower)
                if count > 0:
                    match_count += count
                    matched_keywords.append(keyword)

            if match_count > 0:
                results.append({
                    'id': article['id'],
                    'title': article['title'],
                    'text': article['text'],
                    'match_count': match_count,
                    'matched_keywords': matched_keywords
                })

        # Sort by match count and return top_k
        results.sort(key=lambda x: x['match_count'], reverse=True)
        return results[:top_k]

    def search(self, query: str, top_k: int = 10) -> tuple[list[dict], list[dict], list[str], ApiStatistics]:
        """
        Perform hybrid search: semantic search with embeddings and keyword search.

        Args:
            query: User query
            top_k: Number of top results to return for each search method

        Returns:
            Tuple of (semantic_results, keyword_results, statistics)
        """
        # Expand query to get variations and keywords
        query_versions, keywords, statistics = self.expand_query(query)

        query_debug = []
        query_debug.append(f"\nQuery versions: {query_versions}")
        query_debug.append(f"Keywords: {keywords}\n")

        # Perform semantic search
        semantic_results = self.semantic_search(query_versions, top_k)

        # Perform keyword search
        keyword_results = self.keyword_search(keywords, top_k)

        return semantic_results, keyword_results, query_debug, statistics
