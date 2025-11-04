# Research Paper Analysis: Building a Production-Ready RAG System

```
Paper Title: Building a Production-Ready RAG System from Scratch: An Architectural Deep Dive

1. System Architecture:
   - **Two-Pipeline Design**: Separates offline indexing (asynchronous document processing) from online inference (real-time query handling). This modular approach allows independent scaling and optimization of each component.
   - **Data Flow**: Documents → Chunking → Embedding Generation → PostgreSQL with pgvector storage. Query flow: User Query → Query Embedding → Vector Similarity Search → Context Retrieval → LLM Prompt Augmentation → Response Generation.
   - **Technology Stack**: PostgreSQL with pgvector extension for vector storage, OpenAI API for embeddings (text-embedding-3-small) and generation (gpt-4o), Python for orchestration.
   - **Key Architectural Decision**: Using PostgreSQL+pgvector instead of dedicated vector databases reduces operational complexity while leveraging existing database expertise.

2. Data Preparation & Processing:
   - **Chunking Strategy**: RecursiveCharacterTextSplitter with chunk_size=1000 characters and chunk_overlap=200. This preserves semantic boundaries (paragraphs, sentences) and provides context continuity between chunks.
   - **Embedding Generation**: Uses OpenAI's text-embedding-3-small (1536 dimensions). Batch processing for efficiency during indexing.
   - **Storage Schema**: Simple table structure with document_name, chunk_text, and embedding (VECTOR type) columns. Serial ID for primary key.
   - **Indexing**: HNSW (Hierarchical Navigable Small World) index on embeddings using cosine distance operator. Preferred over IVFFlat for superior query performance despite slower build times.

3. Query Handling & Retrieval Logic:
   - **Query Processing**: User query is embedded using the same model (text-embedding-3-small) to ensure vector space consistency.
   - **Retrieval**: Cosine similarity search using pgvector's `<=>` operator. Top-k parameter (default k=5) controls retrieved context quantity.
   - **Prompt Engineering**: Explicit instruction to answer only from provided context. Includes failure case handling ("I cannot answer...").
   - **Temperature Setting**: Set to 0.0 for deterministic, fact-based responses that minimize creative hallucinations.

4. Implementation Details:
   - **Core Libraries**: `psycopg2` for PostgreSQL connection, `openai` SDK for embeddings/generation, `langchain.text_splitter` for chunking.
   - **SQL Operations**: Direct SQL queries using `psycopg2.cursor()`. Vector similarity via `ORDER BY embedding <=> %s LIMIT %s`.
   - **Embedding API Call**: `openai.embeddings.create(input=chunks, model=EMBEDDING_MODEL)` returns list of embeddings.
   - **LLM API Call**: `openai.chat.completions.create()` with system/user message structure.
   - **Connection Management**: Standard connection pooling recommended (PgBouncer) for production.
   - **Code Pattern**: Functional decomposition with separate functions for indexing, retrieval, prompt construction, and generation.

5. Evaluation & Performance:
   - **Evaluation Metrics Recommended**: Context Precision (relevance of retrieved chunks), Context Recall (completeness of retrieval), Faithfulness (answer adherence to context).
   - **Golden Dataset**: Suggests creating (question, expected_answer, required_context) tuples for systematic evaluation.
   - **Optimization Techniques**: 
     - Hybrid search combining vector search with BM25 keyword search
     - Two-stage re-ranking using cross-encoder models
     - Query caching for identical requests
   - **Scalability Considerations**: Read replicas for PostgreSQL, connection pooling, potential migration to self-hosted models for high throughput.

6. Key Takeaways for System Design:
   - **Critical Design Choice**: Chunk size/overlap significantly impacts retrieval quality—requires empirical tuning per use case.
   - **Same Embedding Model**: Query and document embeddings must use identical models for vector space consistency.
   - **Index Selection**: HNSW preferred over IVFFlat for latency-sensitive applications despite build cost.
   - **Temperature Zero**: Essential for factual QA to prevent hallucinations.
   - **Top-k Tuning**: Balance between retrieval completeness and noise/cost. Start with k=5.
   - **PostgreSQL Advantage**: Reduces infrastructure complexity when vector database expertise is limited.
   - **Production Readiness**: Implement evaluation pipeline, hybrid search, and caching before scaling.
   - **Operational Insight**: Separating indexing from inference enables independent optimization and debugging.

(Total: ~495 words)
```