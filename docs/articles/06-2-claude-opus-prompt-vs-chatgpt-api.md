Concise, implementation-ready summary focused on practical steps to build a hybrid SQL+vector search system using the RRF-based hybrid search approach described in the paper.

1) System Architecture & Design Patterns
- Query Router Design
  - Run parallel queries: a traditional full-text-like (BM25) search and one or more vector queries. The hybrid approach fuses results via Reciprocal Rank Fusion (RRF).
  - Use a single hybrid query payload to Azure Search, combining a textual search string with multiple vectorQueries.
- Integration Pattern
  - Fusion via Reciprocal Rank Fusion (RRF): compute reciprocal ranks across each query result list (textual + vector), sum them per document, and sort by the combined score.
  - Optional post-fusion re-ranking with semantic ranking (@search.rerankerScore) if documents contain semantically rich fields.
  - Weighting: apply vector weights to control the influence of vector results in the final ranking.
- Pipeline Architecture
  - Ingest data into an index with:
    - Text fields indexed as searchable/retrievable (BM25 scoring).
    - Vector fields (e.g., DescriptionVector) for vector search with HNSW.
  - Query path: client input -> hybrid search request (text + vectorQueries) -> RRF fusion -> optional semantic rerank -> return selected fields (select).

2) Data Preparation & Processing
- Text Preprocessing
  - Ensure target text is available in searchable fields and that a corresponding vector field exists (DescriptionVector) for vector queries.
  - Use maxTextRecallSize (default 1,000) to tune how many text results are recalled during hybrid queries.
- Schema Mapping
  - Map structured and unstructured content into a single Azure Search index, marking fields as searchable (for BM25) and retrievable (for results); vector fields must be defined in the index schema.
- Chunking Strategy
  - Not specified in the article; rely on existing data segmentation to produce meaningful vectors in DescriptionVector (i.e., ensure the vector field aligns with logical document granularity).
- Metadata Extraction
  - Include retrievable fields like HotelName, Description, Address/City; rely on search fields and select to surface metadata.

3) Technical Implementation Details
- Embedding Generation
  - Article does not specify embedding models; embeddings are consumed via the vector field (e.g., DescriptionVector). You must generate embeddings externally and store them in the corresponding vector field.
  - k in vector queries: set per-query (e.g., k: 10) to control neighborhood size.
- Vector Storage
  - Vector search in Azure uses HNSW with a chosen similarity metric (Cosine, Euclidean, DotProduct).
  - Index types and configuration: relies on Azure’s vector indexing (HNSW) and the vector field (DescriptionVector).
  - Hybrid scoring: results from vector and text queries are fused via RRF; you can adjust weights for each source.
- SQL Integration
  - The paper’s model maps to a textual/full-text component (BM25) within the index; actual SQL databases aren’t queried directly, but you can treat BM25-like results as the structured/text portion of a hybrid query. For true SQL, you would segment structured data into retrievable/searchable fields in the index or orchestrate separate SQL queries and fuse results via RRF.

4) Query Processing & Optimization
- Query Understanding
  - Accept natural-language input as a text query; optionally enrich with explicit vector-weighting hints.
- Query Rewriting
  - Use the hybrid query payload pattern: a textual “search” string plus one or more vectorQueries with fields, kind, exhaustive, and k.
- Retrieval Strategy
  - top parameter defines unified result count; limit per-source results via k (e.g., k: 10 per vectorQuery, top: 10 overall).
  - Use debug: "vector" to inspect subscores for tuning thresholds; can set debug: "all" to unpack subscores from all sources.
- Performance Optimizations
  - Adjust maxTextRecallSize to balance recall vs. latency; leverage parallel execution of vector and text queries.

5) Result Fusion & Ranking
- Scoring Mechanisms
  - RRF: score per document is influenced by positions in multiple lists; k (e.g., 60) governs the reciprocal rank contribution.
  - Weights: apply vector weight multipliers (e.g., 0.5, 2.0) to modulate vector-source influence.
- Deduplication
  - Not explicitly specified; implement deduplication by document ID post-fusion if duplicates appear across lists.
- Result Presentation
  - Surface fields via select (e.g., HotelName, Description, Address/City) with @search.score; optionally surface @search.rerankerScore after reranking.

6) Practical Libraries & Tools
- Python: azure-search-documents (Azure SDK) for hybrid queries; requests for REST fallbacks.
- Vector/ML: NumPy for basic vector ops and similarity calculations if doing client-side reranking; external embedding generation (not specified in the paper).
- SQL libraries (if mixing in-application SQL): psycopg2/SQLAlchemy to fetch structured data, then fuse with search results.

7) Evaluation Metrics & Testing
- Metrics: use relevance (precision/recall) and surface quality via @search.score; employ subscores from debug to calibrate thresholds.
- Tests: validate with NL queries, compare fused results against ground-truth relevance.

8) Error Handling & Edge Cases
- Failure modes: if one data source returns none, rely on the other source via RRF; use debug to diagnose gaps.
- Ambiguity: detect when parallel sources disagree; fallback to the source with higher confidence or present both sources with caveats.

Key concrete parameters from the paper:
- k in reciprocal rank: ~60 (example).
- vector query sample: k: 10; exhaustive: true; fields: "DescriptionVector".
- top: 10; maxTextRecallSize: default 1000.
- debug: "vector" (to inspect subscores) or "all" for full subscores.
- Use fields marked searchable/retrievable; select returns alongside scores.