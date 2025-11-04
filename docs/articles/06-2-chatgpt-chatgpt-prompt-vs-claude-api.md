```
Paper Title: Hybrid search scoring (RRF) - Azure AI Search | Microsoft Learn

1. System Architecture:
   - Parallel query execution pattern: Multiple queries (full-text BM25 and vector searches) execute simultaneously, then results merge via RRF
   - Modular scoring workflow: Each search method generates independent ranked results with distinct scoring algorithms before fusion
   - Query routing logic: System automatically detects hybrid queries (text + vector) and triggers RRF merging; supports multiple vector fields (e.g., 1 text query + 2 vector queries across 5 fields = 11 parallel executions)
   - Fields must be marked `searchable` for scoring and `retrievable` for inclusion in responses

2. Data Preparation & Processing:
   - Index schema requirements: Fields tagged as `searchable` participate in scoring; `retrievable` fields return in results
   - Vector embeddings: Uses HNSW algorithm with configurable similarity metrics (Cosine, Euclidean, DotProduct)
   - No explicit preprocessing details provided, but implies standard embedding generation for vector fields
   - Storage: Azure AI Search manages indexing; adaptable to FAISS/ChromaDB for custom implementations

3. Query Handling & Retrieval Logic:
   - **RRF Algorithm Core**: For each document in result sets, calculate reciprocal rank score as `1/(rank + k)` where `k=60` (constant, distinct from vector `k` for nearest neighbors)
   - Scoring fusion: Sum reciprocal scores across all result sets per document; rank by combined score
   - Score ranges: BM25 (unbounded), vector (0.333-1.0 for Cosine), RRF (bounded by number of queries × ~1/k)
   - Weighted scoring: Apply multipliers to vector query scores before RRF fusion (e.g., weight=0.5 reduces importance, weight=2.0 increases)
   - Result limiting: Default top 50 (full-text) and `k` (vector); use `maxTextRecallSize` (default 1000) for larger text recall; pagination via `top`, `skip`, `next`

4. Implementation Details:
   - **Direct SDK approach**: Use `openai` for embeddings, `faiss`/`chromadb` for vector storage, `sqlite3`/`psycopg2` for structured data
   - RRF pseudocode:
     ```python
     k = 60  # RRF constant
     for doc in all_results:
         rrf_score = sum(1/(rank_in_resultset + k) for rank_in_resultset in doc.ranks)
     sorted_results = sort(docs, key=rrf_score, reverse=True)
     ```
   - Vector weighting: Multiply initial scores by weight before summing in RRF
   - Debugging: API parameter `debug=vector` or `debug=all` returns subscores for tuning thresholds/weights
   - Semantic reranking (optional): Applies post-RRF with separate `@search.rerankerScore` (range 0-4.0)

5. Evaluation & Performance:
   - Score interpretation: Higher RRF scores indicate consistent high ranking across methods
   - Optimization: Adjust vector weights based on subscore analysis; set `maxTextRecallSize` for recall/latency tradeoffs
   - Pagination reduces response size; default 1000-match limit for full-text (hard cap)
   - Batching/caching not detailed but implied via pagination parameters

6. Key Takeaways for System Design:
   - **Actionable RRF formula**: `1/(rank + 60)` per result set, sum for each document—simple to implement in Python without frameworks
   - **Parallel execution model**: Run SQL (BM25-like) and vector (FAISS/ChromaDB) queries concurrently, merge results via RRF
   - **Vector weighting**: Multiply vector scores pre-fusion to balance text vs. vector importance; use `debug` mode to calibrate
   - **Field-level control**: Mark fields in schema for search/retrieval eligibility; separate vector fields enable multi-vector queries
   - **Scalability**: Limit text recall size and use pagination; monitor query count (text + vector combinations) for performance
   - **Integration with semantic reranking**: Apply RRF first, then optionally rerank top-N with semantic models (e.g., cross-encoders)

(Total ~490 words)
```