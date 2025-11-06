# RAG System Design Without Vector Database

## Overview
This guide covers the design and implementation of a Retrieval-Augmented Generation (RAG) system without using a vector database. This approach stores embeddings in memory or simple files, which works well for smaller to medium-sized document collections.

## 1. Creating Embeddings

For creating embeddings, you have several options:

### Recommended Models:
- **OpenAI's text-embedding-ada-002**: Cost-effective, good performance
- **Sentence Transformers** (open-source): Models like `all-MiniLM-L6-v2` (fast) or `all-mpnet-base-v2` (better quality)
- **Cohere's embed models**: Good multilingual support
- **BGE models**: State-of-the-art open-source models

## 2. Optimal Chunk Size

The optimal chunk size depends on your use case, but here are guidelines:

- **256-512 tokens**: Good for precise retrieval of specific facts
- **512-1024 tokens**: Balanced approach (most common)
- **1024-2048 tokens**: Better for maintaining context in longer passages

### Key Considerations:
- Include overlap between chunks (10-20% overlap)
- Respect natural boundaries (paragraphs, sentences)
- Consider your embedding model's context window

## 3. Storage Strategy

For your use case without a vector database, I recommend:

### Hybrid Approach
Store embeddings in a single searchable structure but maintain article metadata:
- Keep all embeddings in one NumPy array for efficient similarity search
- Maintain metadata mapping chunks to their source articles
- This allows both global search and article-specific filtering

## 4. Example Implementation

Here's a complete working example using Sentence Transformers:

```python
import numpy as np
import json
import pickle
from typing import List, Dict, Tuple
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import re

@dataclass
class Chunk:
    """Represents a text chunk with metadata"""
    text: str
    article_id: str
    article_title: str
    chunk_index: int
    start_char: int
    end_char: int

class SimpleRAGSystem:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the RAG system with a sentence transformer model"""
        self.model = SentenceTransformer(model_name)
        self.chunks: List[Chunk] = []
        self.embeddings: np.ndarray = None
        
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Input text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Number of overlapping characters between chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            # Find the end of the chunk
            end = start + chunk_size
            
            # If we're not at the end of the text, try to break at a sentence
            if end < len(text):
                # Look for sentence ending punctuation
                last_period = text.rfind('.', start, end)
                last_question = text.rfind('?', start, end)
                last_exclaim = text.rfind('!', start, end)
                
                # Find the last sentence boundary
                last_sentence = max(last_period, last_question, last_exclaim)
                
                if last_sentence > start:
                    end = last_sentence + 1
            
            chunks.append(text[start:end].strip())
            
            # Move start position with overlap
            start = end - overlap if end < len(text) else end
            
        return chunks
    
    def process_articles(self, articles: List[Dict[str, str]], 
                        chunk_size: int = 512, overlap: int = 50):
        """
        Process multiple articles and create embeddings
        
        Args:
            articles: List of dicts with 'id', 'title', and 'content' keys
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
        """
        all_chunks = []
        
        for article in articles:
            # Chunk the article
            text_chunks = self.chunk_text(article['content'], chunk_size, overlap)
            
            # Create Chunk objects with metadata
            for idx, chunk_text in enumerate(text_chunks):
                chunk = Chunk(
                    text=chunk_text,
                    article_id=article['id'],
                    article_title=article['title'],
                    chunk_index=idx,
                    start_char=idx * (chunk_size - overlap),
                    end_char=min(idx * (chunk_size - overlap) + chunk_size, 
                                len(article['content']))
                )
                all_chunks.append(chunk)
        
        self.chunks = all_chunks
        
        # Create embeddings for all chunks
        chunk_texts = [chunk.text for chunk in self.chunks]
        self.embeddings = self.model.encode(chunk_texts, 
                                           convert_to_numpy=True,
                                           show_progress_bar=True)
        
        print(f"Processed {len(articles)} articles into {len(self.chunks)} chunks")
    
    def search(self, query: str, top_k: int = 5, 
               article_filter: str = None) -> List[Tuple[Chunk, float]]:
        """
        Search for relevant chunks
        
        Args:
            query: Search query
            top_k: Number of top results to return
            article_filter: Optional article ID to filter results
        """
        if self.embeddings is None:
            raise ValueError("No articles have been processed yet")
        
        # Encode the query
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Calculate cosine similarities
        similarities = np.dot(self.embeddings, query_embedding.T).flatten()
        
        # Filter by article if specified
        if article_filter:
            mask = np.array([chunk.article_id == article_filter 
                           for chunk in self.chunks])
            similarities = similarities * mask - (1 - mask)  # Set non-matching to -1
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Return chunks with their similarity scores
        results = []
        for idx in top_indices:
            if similarities[idx] > -1:  # Skip filtered-out results
                results.append((self.chunks[idx], float(similarities[idx])))
        
        return results
    
    def save_index(self, filepath: str):
        """Save the embeddings and chunks to disk"""
        data = {
            'chunks': self.chunks,
            'embeddings': self.embeddings
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        print(f"Index saved to {filepath}")
    
    def load_index(self, filepath: str):
        """Load embeddings and chunks from disk"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        self.chunks = data['chunks']
        self.embeddings = data['embeddings']
        print(f"Index loaded from {filepath}")

# Example usage
def main():
    # Initialize the RAG system
    rag = SimpleRAGSystem(model_name='all-MiniLM-L6-v2')
    
    # Sample articles
    articles = [
        {
            'id': 'article_1',
            'title': 'Introduction to Machine Learning',
            'content': '''Machine learning is a subset of artificial intelligence that 
            enables systems to learn and improve from experience without being explicitly 
            programmed. It focuses on developing computer programs that can access data 
            and use it to learn for themselves. The process of learning begins with 
            observations or data, such as examples, direct experience, or instruction, 
            in order to look for patterns in data and make better decisions in the future. 
            The primary aim is to allow the computers to learn automatically without 
            human intervention or assistance and adjust actions accordingly.'''
        },
        {
            'id': 'article_2',
            'title': 'Deep Learning Fundamentals',
            'content': '''Deep learning is a subset of machine learning that uses 
            artificial neural networks with multiple layers. These layers progressively 
            extract higher-level features from raw input. For example, in image processing, 
            lower layers may identify edges, while higher layers may identify human faces. 
            Deep learning has dramatically improved the state-of-the-art in speech 
            recognition, visual object recognition, object detection, and many other 
            domains. It has been able to achieve human-level performance in certain 
            narrow domains.'''
        }
    ]
    
    # Process articles
    rag.process_articles(articles, chunk_size=200, overlap=30)
    
    # Search examples
    queries = [
        "What is machine learning?",
        "How do neural networks learn features?",
        "automatic learning without human intervention"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: {query}")
        results = rag.search(query, top_k=3)
        
        for i, (chunk, score) in enumerate(results, 1):
            print(f"\n  Result {i} (Score: {score:.3f})")
            print(f"  Article: {chunk.article_title}")
            print(f"  Text: {chunk.text[:150]}...")
    
    # Save the index for later use
    rag.save_index('rag_index.pkl')
    
    # Example of loading and searching
    new_rag = SimpleRAGSystem()
    new_rag.load_index('rag_index.pkl')
    results = new_rag.search("What is deep learning?", top_k=2)
    print(f"\n✅ Loaded index works! Found {len(results)} results")

if __name__ == "__main__":
    main()
```

## Additional Optimizations

For production use, consider these enhancements:

### 1. Batch Processing for Large Document Sets

```python
def process_articles_batch(self, articles, batch_size=32):
    """Process articles in batches to manage memory"""
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]
        self.process_articles(batch)
```

### 2. Hybrid Search Combining Semantic and Keyword Search

```python
def hybrid_search(self, query, top_k=5, alpha=0.7):
    """Combine semantic search with BM25 keyword search"""
    # Semantic search results
    semantic_results = self.search(query, top_k * 2)
    
    # BM25 or TF-IDF search (you'd implement this)
    keyword_results = self.keyword_search(query, top_k * 2)
    
    # Combine scores with weighting
    combined_scores = {}
    for chunk, score in semantic_results:
        combined_scores[chunk] = alpha * score
    
    for chunk, score in keyword_results:
        if chunk in combined_scores:
            combined_scores[chunk] += (1 - alpha) * score
        else:
            combined_scores[chunk] = (1 - alpha) * score
    
    # Return top-k combined results
    return sorted(combined_scores.items(), 
                 key=lambda x: x[1], reverse=True)[:top_k]
```

### 3. Use FAISS for Faster Similarity Search

```python
import faiss

def build_faiss_index(embeddings):
    """Build a FAISS index for faster search"""
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    
    return index
```

## Key Recommendations

1. **Start simple**: Begin with the basic implementation above and optimize as needed
2. **Monitor performance**: Track search latency and accuracy
3. **Consider scaling**: When you reach ~100k chunks, consider transitioning to a proper vector database (Pinecone, Weaviate, Qdrant)
4. **Preprocessing**: Clean and normalize text before chunking (remove extra whitespace, handle special characters)
5. **Evaluation**: Implement metrics to measure retrieval quality (precision@k, recall@k)

## Performance Considerations

This approach works well for:
- Up to ~10,000 articles (depending on chunk size)
- Applications where sub-100ms search latency is acceptable
- Use cases where you need full control over the retrieval pipeline

For larger scales, consider:
- Vector databases (Pinecone, Weaviate, Qdrant, Milvus)
- More sophisticated indexing strategies (HNSW, IVF)
- Distributed processing frameworks

## Dependencies

Install required packages:

```bash
pip install sentence-transformers numpy faiss-cpu
# For GPU support: pip install faiss-gpu
```

## Conclusion

This implementation provides a solid foundation for a RAG system without requiring a vector database. It's suitable for proof-of-concepts, small to medium deployments, and situations where you need full control over the retrieval process. As your needs grow, you can easily transition to more sophisticated solutions while keeping the same chunking and embedding strategies.