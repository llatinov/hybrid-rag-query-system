# Research Paper Analysis Prompt for Hybrid Search System Implementation

## Instructions
Analyze the following research paper and extract **practical implementation details** for building a system that answers user questions by querying both structured databases (SQL) and unstructured text (vector search). Focus on actionable insights that can be directly applied using low-level SDKs like OpenAI's library, without relying on high-level frameworks like LangChain or LlamaIndex.

## Required Extraction Points (500 words max)

### 1. System Architecture & Design Patterns
- **Query Router Design**: How does the paper suggest determining whether to use SQL, vector search, or both?
- **Integration Pattern**: What specific approach is used to combine results from structured and unstructured sources?
- **Pipeline Architecture**: What are the key components and their interaction flow?

### 2. Data Preparation & Processing
- **Text Preprocessing**: What specific techniques are mentioned for preparing unstructured data for vectorization?
- **Schema Mapping**: How is the relationship between structured and unstructured data maintained?
- **Chunking Strategy**: What text segmentation approach is recommended (chunk size, overlap, metadata preservation)?
- **Metadata Extraction**: What metadata should be extracted and stored alongside vectors?

### 3. Technical Implementation Details
- **Embedding Generation**:
  - Recommended embedding models and dimensions
  - Batch processing strategies
  - Cost optimization techniques
- **Vector Storage**:
  - Specific vector database recommendations (Pinecone, Weaviate, Qdrant, pgvector, etc.)
  - Index types (HNSW, IVF, etc.) and configuration parameters
  - Hybrid search scoring mechanisms
- **SQL Integration**:
  - Query generation techniques
  - Schema inference methods
  - SQL sanitization and validation approaches

### 4. Query Processing & Optimization
- **Query Understanding**: Methods for parsing user intent and determining data source requirements
- **Query Rewriting**: Techniques for transforming natural language to SQL/vector queries
- **Retrieval Strategy**:
  - Similarity threshold values
  - Top-k selection criteria
  - Re-ranking algorithms
- **Performance Optimizations**: Caching strategies, parallel processing, or query optimization techniques

### 5. Result Fusion & Ranking
- **Scoring Mechanisms**: How to combine confidence scores from SQL and vector results
- **Deduplication**: Strategies for handling overlapping information
- **Result Presentation**: Formatting and structuring combined results

### 6. Practical Libraries & Tools
- **Specific Python libraries** mentioned (beyond OpenAI SDK)
- **SQL libraries**: SQLAlchemy, psycopg2, etc.
- **Vector processing tools**: NumPy operations, similarity calculation methods
- **Utility libraries**: For text processing, data validation, etc.

### 7. Evaluation Metrics & Testing
- **Quality metrics**: Precision, recall, relevance scoring methods
- **Performance benchmarks**: Latency targets, throughput considerations
- **Testing strategies**: Dataset preparation, validation approaches

### 8. Error Handling & Edge Cases
- **Failure modes**: Common issues and mitigation strategies
- **Ambiguity handling**: Dealing with unclear queries
- **Fallback mechanisms**: When one data source fails

## Output Format
Provide a **concise summary** (max 500 words) focusing on:
1. **Most actionable insights** that can be immediately implemented
2. **Specific configuration values** or parameters mentioned
3. **Code patterns or pseudo-code** if provided
4. **Unique contributions** this paper makes to the hybrid search problem
5. **Gaps or limitations** acknowledged that need alternative solutions

**Prioritize practical, implementation-ready details over theoretical discussions.**
