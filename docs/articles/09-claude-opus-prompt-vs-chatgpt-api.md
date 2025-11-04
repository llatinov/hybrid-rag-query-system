Here are the practical, implementation-ready insights from the paper “RAG-based Question Answering over Heterogeneous Data and Text” (Quasar), focused on building a SQL + vector-search hybrid system with concrete, low-level guidance.

1) System Architecture & Design Patterns
- Query Router Design (SI-driven routing)
  - Generate a Structured Intent (SI) with slots: Ans-Type, Entities, Time, Location, Relation (optional additional cues).
  - Use SI to guide retrieval from KG, text docs, and tables; SAU (Question Understanding) precedes Evidence Retrieval (ER).
- Integration Pattern (unified evidence then generation)
  - Retrieve from all sources in parallel, then Iterative Re-Ranking & Filtering (RF) to select a small, high-quality evidence set; feed top-k to Answer Generation (AG).
  - Score fusion: combine source-agnostic scores (BM25 for linearized content) with cross-encoder/GNN-derived scores in RF.
- Pipeline Architecture & Components
  - QU: Question Understanding (SI extraction) using a small LM, leading to SI.
  - ER: Evidence Retrieval from KG (Clocq), text, and tables; evidence verbalized into token sequences.
  - RF: Two options for re-ranking: Graph Neural Network (GNN) or Cross-Encoder (CE) with BM25 baselines; two-stage pruning (e.g., 1000 → 30).
  - AG: Retrieval-Augmented Generation with a small-scale LLM (Llama 3.1 8B-Instruct) plus prompt, outputting answer + evidence snippets.

2) Data Preparation & Processing
- Text Preprocessing & Verbalization
  - Linearize and verbalize results: KG as BFS-traversed triples; tables as rows with headers and DOM-path context; raw text as token sequences (prefix with article/table context).
- Schema Mapping
  - SI slots anchor downstream queries to KG, text, and tables; maintain linking metadata per evidence item (entity IDs, table IDs, sentence IDs).
- Chunking Strategy
  - Treat each table row as a chunk; sentences from text as chunks; pool evidence and index into a single, on-the-fly corpus for retrieval.
- Metadata Extraction
  - Preserve: KG disambiguations, temporal/seasonal qualifiers, table headers, DOM-paths, article provenance, and per-evidence provenance tags.
  
3) Technical Implementation Details
- Embedding Generation
  - Embedding/Scoring models: cross-encoder embeddings to initialize node encodings; CE models (MS-MARCO MiniLM-L-4-v2 and MiniLM-L-6-v2) for CE-based RF.
  - Embedding dimensions: 768 (typical for MiniLM).
  - Batch processing: CE-based scoring can reuse batched inputs during RF; training uses small batch sizes (e.g., 8) with warm-up ratio ~0.01.
  - Cost optimization: split RF into two mini-rounds (top-1000 → top-30) to keep LLM cost manageable.
- Vector Storage (recommendations beyond the paper’s text-centric approach)
  - Vector DB options: Pinecone, Weaviate, Qdrant, or pgvector.
  - Index types: HNSW (default high-accuracy) or IVF-like structures; tune ef (recall) and M (connectivity).
  - Hybrid search: store vector embeddings for textual/table evidence; combine with BM25 or CE scores in RF.
- SQL Integration (actionable pattern)
  - Query generation: map SI slots to restrictive SQL clauses over internal tabular data stores (if present). Example approach: derive WHERE clauses from Entities, Time, Location, and Relation; parameterize to prevent injections.
  - Schema inference: infer table schemas from the evidence (column names → features) and align with SI fields.
  - Sanitization/validation: use prepared statements, parameter binding, and explicit type checks; validate user-driven filters before execution.

4) Query Processing & Optimization
- Query Understanding & Rewriting
  - QU uses a small LM to produce SI; reuse this SI to drive separate KG/text/table queries.
- Retrieval Strategy
  - ER: KG (Clocq) queries built from SI slots; Text/Table retrieval via BM25 over linearized content; top-k = 1000.
  - RF: two rounds to prune to top-30 or top-10; optionally CE-based or GNN-based re-ranking.
- Performance Optimizations
  - Batch ER/RF scoring; parallelize multi-source retrieval; cache frequent SI-to-evidence mappings; batch LLM calls in AG when possible.

5) Result Fusion & Ranking
- Scoring & Fusion
  - Combine BM25 scores with CE/GNN-derived relevance in RF; normalize across sources for fair fusion.
- Deduplication
  - Merge overlapping evidence (e.g., same entity from multiple sources) to avoid repeated snippets; keep succinct citation metadata.
- Result Presentation
  - Return: final answer, confidence cue, and top evidence snippets with source IDs and short quotes.

6) Practical Libraries & Tools
- Core: Hugging Face transformers, PyTorch; LLaMA-3.1-8B-Instruct for AG; BART-base (fine-tuned) for QU.
- Data/Retrieval: Clocq for KG disambiguation; Explaignn (Quasar codebase) for QU/ER/RF; FAISS/other vector libs for vector indexing (if chosen).
- Vector processing: NumPy for scoring and normalization.
- SQL: SQLAlchemy or psycopg2 for internal DB interactions; use prepared statements.

7) Evaluation Metrics & Testing
- Metrics: P@1, AP@k, MRR@k; automatic answer presence (AP@k) and human-annotated correctness (as in Crag/TimeQuestions/CompMix).
- Testing: cross-bench with CompMix, TimeQuestions, Crag; ablations to quantify impact of RF, SI quality, and source mix.

8) Error Handling & Edge Cases
- Failure modes: ER recall gaps on long-tail or aggregative questions; RF misranking; AG hallucination on noisy snippets.
- Ambiguity handling: faithful abstention when evidence is insufficient (unknown); SI-guided disambiguation via QU.
- Fallbacks: if a source fails, degrade gracefully to remaining sources; if all fail, return known-minimal answer or unknown.

Gaps/Limitations
- ER recall remains a bottleneck for large aggregations; TimeQuestions shows temporal reasoning strengths; Crag needs broader web sources.
- Trust in data sources is assumed; in production, add reliability scoring and conflict-resolution mechanisms.