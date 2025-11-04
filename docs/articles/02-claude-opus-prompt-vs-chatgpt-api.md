Concise, actionable synthesis for implementing a hybrid SQL + vector-search system inspired by the paper "RAG-Fusion: a New Take on Retrieval-Augmented Generation."

1) System Architecture & Design Patterns
- Query Router Design
  - Use two paths: structured (SQL) for precise attribute queries; unstructured (vector search) for document-level knowledge. RAG-Fusion-like flow suggests generating multiple NLQs to broaden coverage; apply to unstructured retrieval primarily.
  - Ambiguity/intent handling: detect when a user clearly seeks a structured attribute (e.g., IP rating, part number) vs. when they need document-based knowledge or product context; route accordingly, with a fallback to hybrid when both are relevant.
- Integration Pattern
  - Hybrid fusion: retrieve documents via vector search for multiple generated queries, compute Reciprocal Rank Fusion (RRF) scores across sources, accumulate scores per document, then pass top docs along with the queries to the LLM to produce the answer.
  - For structured data, fetch SQL results, then optionally enrich with unstructured docs; fuse signals in a final ranking stage before presenting results.
- Pipeline Architecture
  - Components: (A) NLQ processor, (B) SQL engine (with sanitization), (C) embedding generator, (D) vector DB (with metadata), (E) result reranker (RRF), (F) LLM for final answer, (G) orchestrator/router.

2) Data Preparation & Processing
- Text Preprocessing
  - Convert PDFs/datasheets to text; plan for later multimodal-to-text conversion; preserve metadata (source, document id, section, page).
- Schema Mapping
  - Establish a shared ID/annotation system so structured and unstructured sources can be tied (e.g., document_id aligns with metadata entries and retrieval results).
- Chunking Strategy
  - The paper implies chunking documents for vectorization; exact sizes/overlaps aren’t specified. Use standard practices (e.g., overlapping chunks) and retain chunk-level metadata (source, position, etc.).
- Metadata Extraction
  - Store: document_id, source type, page/section, product identifiers, and any domain attributes (e.g., IP rating, SNR). Attach to each vector embedding as metadata for later filtering.

3) Technical Implementation Details
- Embedding Generation
  - Models/dimensions: not specified in the paper; treat as model- and API-dependent. Use batch processing for embeddings; ensure per-batch size aligns with API/GPU limits.
  - Cost optimization: batch queries; reuse embeddings when possible; consider local/edge hosting to reduce latency (as noted for LLM calls).
- Vector Storage
  - DBs recommended: Pinecone, Weaviate, Qdrant, pgvector (explicitly mentioned).
  - Index types: HNSW, IVF (as options); tune for recall vs. latency.
  - Hybrid search scoring: implement RRF (see below) to fuse results from multiple NL-generated queries; store per-document metadata for downstream filtering.
- SQL Integration
  - Query generation: leverage LLMs to produce parameterized SQL from NL queries; sanitize via parameterization; validate against a curated schema.
  - Schema inference: use sample NLQs and metadata to map to tables/columns; maintain a whitelist of allowed operations and tables.
  - Sanitization: prefer prepared statements (e.g., psycopg2/SQLAlchemy core) and input validation.

4) Query Processing & Optimization
- Query Understanding
  - Generate multiple queries from the original NLQ to broaden retrieval (as in RAG-Fusion).
- Query Rewriting
  - Produce both SQL (for structured) and NL/LP prompts for vector retrieval; feed these to LLMs with the relevant context.
- Retrieval Strategy
  - Vector: top-n per generated query; apply a similarity threshold to prune weak hits.
  - Re-ranking: apply Reciprocal Rank Fusion: rrfscore = 1 / (rank + k); accumulate per document across queries.
- Performance Optimizations
  - Consider local LLM hosting to reduce latency; resize the number of generated queries to balance quality and speed.

5) Result Fusion & Ranking
- Scoring Mechanisms
  - Combine SQL results (structured confidence) with RRF-ranked vector results; weigh by source reliability and recency.
- Deduplication
  - Merge overlapping docs by document_id; keep highest-scoring instance.
- Presentation
  - Present a unified answer with citations to both structured attributes and retrieved documents; explain when information is inferred or context-providing.

6) Practical Libraries & Tools
- Python: OpenAI library for LLM calls; SQL libraries (psycopg2, SQLAlchemy core for safe SQL); vector DB clients (Pinecone, Weaviate, Qdrant, pgvector).
- Vector processing: NumPy for simple scoring, and built-in distance functions.
- Evaluation: RAGElo, Ragas for automated/episodic evaluation; human-in-the-loop for complex cases.

7) Evaluation Metrics & Testing
- Metrics: accuracy, relevance, comprehensiveness (human-evaluated); traditional automated metrics limited for hybrid tasks.
- Benchmarks: latency targets; measure runtime per query; document retrieval quality; track when RRF causes drift.

8) Error Handling & Edge Cases
- Failure modes: queries drifting off-topic due to extraneous generated queries.
- Ambiguity: prompt engineering guidance; fallback to more conservative prompts.
- Fallbacks: if structured data missing, rely on vector results; if vector retrieval fails, return structured data if possible; otherwise present a best-effort answer with caveats.

Gaps/Limitations: The paper focuses on RAG-Fusion for unstructured docs; it provides limited concrete SQL guidance or numeric hyperparameters. Expect iterative tuning for your data, and monitor for off-topic regeneration and bilingual/multilingual support challenges. 

Code pattern (pseudo):
- process_query(Q):
  - sql_results = run_sql_from_nl(Q)  // parameterized, safe
  - gen_queries = LLM_generate_queries(Q)
  - vec_docs = [vector_search(g) for g in gen_queries]
  - fuse = RRFReranker(vec_docs, sql_results)
  - final_queries = LLM_generate_answer(Q, fuse.top_docs)
  - return format(final_queries)