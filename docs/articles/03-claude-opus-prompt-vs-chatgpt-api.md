Concise practical summary for building a SQL + vector hybrid QA system (inspired by DeKeySQL/DeKeyNLU)

1) System Architecture & Design Patterns
- Query Router Design
  - Use a two-stage, task-understanding driven flow: first, UQU decomposes the user question into a main task and sub-tasks and extracts keywords; these guide whether to route to SQL-structured reasoning (NL2SQL) and/or vector-based retrieval.
  - In practice: always run UQU, then feed results to Entity Retrieval (vector) and Generation (SQL) steps. Larger decomposition tasks benefit from GPT-4o-family models; keyword extraction benefits from smaller models (e.g., Mistral-7B).
- Integration Pattern
  - Modular RAG pipeline: UQU (understanding) -> Entity Retrieval (retrieves schema elements and descriptions) -> Generation (SQL) with revision loop for correction.
  - Retrieval outputs (tables/columns/descriptions) are fed into the SQL prompt as schema context; a revision module corrects errors before execution.
- Pipeline Architecture
  - Three core modules: User Question Understanding (UQU), Entity Retrieval, Generation (with Revision).
  - Data flows: question -> UQU outputs + keywords ->Entity Retrieval returns metadata (tables/columns/descriptions) ->Generation builds initial SQL with evidence + retrieved entities ->Revision fixes errors -> execute SQL to answer.

2) Data Preparation & Processing
- Text Preprocessing
  - Keyword extraction splits into object (table/column names) and implementation (filters, conditions as key-value pairs).
  - Descriptions or textual data related to columns/values are prepared as metadata for embedding retrieval.
- Schema Mapping
  - After retrieval, cross-reference keywords to concrete table/column names; de-duplicate and categorize to map unstructured hints to the structured schema.
- Chunking Strategy
  - Not chunking large documents here; leverage column/value descriptions as compact metadata. For larger textual data, plan embedding segments with consistent metadata (not specified in the paper).
- Metadata Extraction
  - Capture: object keywords (tables/columns), implementation keywords (filters), and textual descriptions for columns/values; preserve evidence cues used in prompts.

3) Technical Implementation Details
- Embedding Generation
  - Recommended embeddings: text-embedding-3-large, Stella-400M (and Stella-1.5B as alternatives).
  - Batch processing: not explicitly specified; use reasonable batch sizes (e.g., 32–128) for embedding generation and indexing.
  - Cost optimizations: use smaller embedding models for retrieval (e.g., Stella-400M) when possible; reserve larger models (or GPT-based prompts) for generation tasks.
- Vector Storage
  - Vector DB: Chroma used to store table data (entity embeddings and metadata).
  - Index types/config: MinHash for fast, scalable approximate matching on column names and values; BM25 as an alternative for exact-ish lexical matching.
  - Hybrid search scoring: retrieve top-5 candidates by embedding similarity (MinHash/Jaccard or BM25), then re-rank to top-2 with a dedicated re-ranker model.
- SQL Integration
  - Query generation techniques: prompt templates that include data schema, user question, UQU outputs (main/sub-tasks), and retrieved entities; use in-context learning (ICL) with these prompts to generate SQL.
  - Schema inference: rely on retrieved schema elements to constrain the SQL (JOINs, GROUP BY, etc.).
  - SQL sanitization/validation: use a Revision module; feed erroneous SQL and error messages back to an LLM for correction; cap revision iterations (threshold) to manage cost.

4) Query Processing & Optimization
- Query Understanding
  - UQU performs task decomposition (main task + sub-tasks) and keyword extraction (object vs implementation) to infer data sources and filtering logic.
- Query Rewriting
  - Use CoT-style prompts guiding the generation model; structure prompts with data schema, reasoning steps, constraints, and incentives to reduce errors.
- Retrieval Strategy
  - Retrieve top-5 candidates for both tables/columns and descriptions; use a re-ranker to select the top-2.
  - Thresholds: numeric keywords use exact matches; purely text/numeric mixed keywords use top-5 with no threshold.
- Performance Optimizations
  - Fine-tuning: UQU model with DeKeyNLU yields large accuracy gains; larger models help task decomposition, smaller models help keyword extraction.
  - Revision module: calibrate and cap iterations (optimal threshold around 3) to balance accuracy, time, and cost.

5) Result Fusion & Ranking
- Scoring Mechanisms
  - Final SQL is evaluated by executing it; semantic correctness is measured via execution results (EX). GPT-4o scoring is calibrated against human judgments.
  - Use the Revision output to tighten correctness before execution.
- Deduplication
  - After retrieval, deduplicate and classify retrieved entities (tables/columns) to avoid conflicting sources.
- Result Presentation
  - Present the final executed results; provide the SQL used and a brief explanation of the reasoning (optional, depending on UI).

6) Practical Libraries & Tools
- Python libraries: OpenAI API (for UQU, generation, revision), Chroma (vector DB), MinHash/Jaccard, BM25 (retrieval baselines).
- SQL libraries: SQLAlchemy, psycopg2 (or equivalent) for executing generated SQL.
- Vector processing: NumPy for similarity, cosine similarity utilities.
- Utility/tools: Krippendorff’s Alpha (QA consistency), calibration helpers for GPT-4o scores.

7) Evaluation Metrics & Testing
- Quality metrics: Execution Accuracy (EX), BLEU/ROUGE for task reasoning, GPT-4o score (calibrated), F1 for keyword extraction.
- Performance: report latency, time per revision, and system cost; 70/20/10 train/val/test splits; 3-round cross-validation; Krippendorff’s Alpha ~0.76.
- Testing: compare against open NL2SQL baselines; validate across multiple datasets (BIRD, Spider).

8) Error Handling & Edge Cases
- Failure modes: incorrect column names, missing GROUP BY/DISTINCT/RANK, incorrect evidence adherence, incorrect filtering, ambiguous sub-tasks.
- Mitigations: a revision module with error feedback; calibrated GPT-4o scoring to align automated judgments with humans; cap revision iterations to control cost.
- Fallbacks: if retrieval or generation yields errors, rely on revision prompts and execute-once validation; consider re-running UQU or retrieval with adjusted prompts if needed.

Gaps/Limitations
- DeKeyNLU’s 1,500-sample size limits generalization; need dataset expansion and adaptive task granularity.
- Evaluation relies on large LLMs; explore more cost-efficient RAG configurations and larger schema generalization to unseen databases.