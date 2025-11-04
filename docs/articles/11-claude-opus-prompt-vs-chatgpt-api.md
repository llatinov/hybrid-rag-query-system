I can’t access the article due to a 403 error, so I can’t extract paper-specific details. Here is a concise, implementation-ready blueprint for a hybrid SQL + vector search system, focusing on concrete patterns, parameters, and code-facing guidance you can apply today. If you share accessible excerpts or the full text, I’ll tailor this to the paper’s specifics.

1) System Architecture & Design Patterns
- Query Router Design: classify intent into structured (SQL-relevant), unstructured (vector-relevant), or hybrid. Use a lightweight intent classifier or rule-based extractor that separates: (a) filters, aggregates, joins → SQL; (b) semantic query portion → vector; (c) both → run both paths.
- Integration Pattern: late fusion with score normalization. Retrieve SQL results and vector results, normalize scores to [0,1], compute final_score = w_sql*score_sql + w_vec*score_vec, and re-rank.
- Pipeline Architecture: Query Parser → SQL Engine → Embedding Generator (or reuse cached embeddings) → Vector DB → Retriever → Re-ranker → Result Formatter → Client.

2) Data Preparation & Processing
- Text Preprocessing: clean HTML/markup, normalize whitespace, lowercasing where appropriate; retain metadata (doc_id, source, date). For embeddings, tokenize with the model’s tokenizer; avoid aggressive stemming that breaks alignment with metadata.
- Schema Mapping: maintain a mapping table linking structured records to text chunks (doc_id ↔ chunk_id) so you can join results later. Preserve provenance fields (source, table, column names).
- Chunking Strategy: 500–750 tokens per chunk with ~100–200 token overlap; store metadata: doc_id, chunk_id, position, origin_text_snippet.
- Metadata Extraction: document_id, chunk_id, source, document_type, date, author, embedding_dim, language, original_text.

3) Technical Implementation Details
- Embedding Generation:
  - Models & dimensions: commonly 1536-dim embeddings (e.g., OpenAI ada-002/text-embedding-3); consider smaller models for cost if latency is critical.
  - Batch processing: batch_size 128–256 embeddings per API call; implement exponential backoff on API errors.
  - Cost optimization: cache embeddings by doc_id/chunk_id; precompute during indexing; deduplicate identical chunks.
- Vector Storage:
  - Recommendations: Weaviate, Pinecone, Qdrant, or pgvector (PostgreSQL extension).
  - Index types: HNSW (default in Weaviate/Qdrant/Pinecone); IVF is optional for very large corpora. Typical: HNSW with M=16–32, efConstruction=200–300; query-time ef=200–300.
  - Hybrid scoring: store metadata fields with vectors (doc_id, chunk_id, source). Enable cosine similarity (or dot product) as vector_score; combine with SQL-derived confidence.
- SQL Integration:
  - Query generation: build parameterized SQL using schema introspection; for NL → SQL, implement a lightweight template-based or rule-based builder with validation.
  - Schema inference: query PostgreSQL/MySQL's information_schema to enumerate tables/columns; cache schema for indexing.
  - Sanitization: always use prepared statements; validate user input against allowed columns and sanitized values.

4) Query Processing & Optimization
- Query Understanding: extract intent, required columns, filters, and time ranges; detect whether a vector search is needed (semantic intent) vs. strict structural constraints.
- Query Rewriting: NL → SQL via rule-based mapping (e.g., “show orders in last 30 days where amount > X”); NL → vector query by embedding the NL query and searching the vector index.
- Retrieval Strategy: vector_top_k = 5–10; SQL_top_k = 10–50; similarity_threshold = 0.75–0.85 (cosine); parallelize SQL and vector fetch; re-rank with hybrid score.
- Performance Optimizations: parallelize retrieval, async I/O, result caching for frequent queries, batched embedding generation, pagination to limit latency.

5) Result Fusion & Ranking
- Scoring: final_score = w_sql*score_sql + w_vec*score_vec (tune w_sql, w_vec, e.g., 0.4/0.6); normalize across sources.
- Deduplication: dedupe by doc_id and chunk_id; keep highest-scoring chunk per source-doc pair.
- Presentation: provide fields: title/snippet, source, data_source_type (SQL/Vector/Both), score, provenance, and a link or reference.

6) Practical Libraries & Tools
- Python: psycopg2 or SQLAlchemy; vector clients (weaviate-client, pinecone-client, qdrant-client, pgvector); OpenAI Python SDK; NumPy; tiktoken for token counting; spaCy/NLTK for light NLP.
- Utilities: rapidfuzz for fuzzy matching; pandas for tabular handling; asyncio/async libs for concurrency.
- Data validation: pydantic; simple logging and metrics collection.

7) Evaluation Metrics & Testing
- Quality: precision@k, recall@k, NDCG@k; relevance judgments via human evaluation.
- Performance: end-to-end latency targets (e.g., <1s for common queries, <3s worst-case); throughput goals (qps with indexing and caching).
- Testing: unit tests for SQL generation, embedding/matching correctness; dataset with known NL→SQL/semantic queries; ablation studies for source fusion.

8) Error Handling & Edge Cases
- Failure modes: vector DB downtime, SQL downtime, embedding API limits; implement fallbacks (vector only or SQL only) with partial results.
- Ambiguity: ask clarifying questions or provide ranked options with source hints.
- Retries & Backoffs: exponential backoff, circuit breakers for external services; cache negative results to avoid repeated failing calls.

If you can provide accessible text or sections from the article, I’ll tailor these points to its exact approaches and terminology.