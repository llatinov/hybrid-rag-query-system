```
Paper Title: DeKeyNLU: Enhancing Natural Language to SQL Generation through Task Decomposition and Keyword Extraction

1. System Architecture:
   - **Modular RAG-based Pipeline (DeKeySQL)**: Three core modules: (1) User Question Understanding (UQU), (2) Entity Retrieval, and (3) Generation (with Revision).
   - **Data Flow**: User question → UQU (task decomposition + keyword extraction) → Entity Retrieval (database matching) → Generation (SQL creation) → Revision (error correction) → Final SQL execution.
   - **No High-Level Frameworks**: Explicitly uses low-level SDKs like `openai`, `sqlite3`, embedding models directly (Stella, text-embedding-3-large), retrieval methods (MinHash, BM25), and custom indexing (Chroma database).
   - **Routing Logic**: Keywords categorized into "object" (table/column names) and "implementation" (filtering criteria as key-value pairs) to guide retrieval and generation.

2. Data Preparation & Processing:
   - **Dataset Creation (DeKeyNLU)**: 1,500 annotated QA pairs from BIRD dataset; manual refinement of GPT-4o pre-annotations through 3-round cross-validation by expert annotators.
   - **Annotation Structure**: Task decomposition (main task + sub-tasks) and keyword extraction (object + implementation dictionaries).
   - **Text Processing**: Chain-of-Thought (CoT) prompts for task decomposition; few-shot learning for keyword extraction.
   - **Entity Indexing**: Database schema elements (table/column names, values, descriptions) encoded and stored in Chroma vector database using embedding models (Stella-400M, Stella-1.5B, text-embedding-3-large).
   - **Hybrid Retrieval Preparation**: MinHash + Jaccard Score for column names; BM25 for table values; exact matching for numeric keywords; cosine similarity for textual descriptions.

3. Query Handling & Retrieval Logic:
   - **Query Parsing**: User question processed via fine-tuned LLM (e.g., GPT-4o-mini, Mistral-7B) to extract structured tasks and keywords.
   - **Hybrid Retrieval**:
     - **Database Retrieval**: MinHash/BM25 retrieves top-5 column names and table values (score > 0); re-ranker selects top-2.
     - **Description Retrieval**: Embedding model + cosine similarity for top-5 descriptions; re-ranker finalizes relevance.
   - **Ranking/Fusion**: Two-stage retrieval + re-ranking ensures precision; de-duplication and categorization of retrieved entities before generation.
   - **Prompt Engineering**: Generation prompts include schema, user question, decomposed tasks, retrieved entities, constraints, and incentives (few-shot ICL).

4. Implementation Details:
   - **Libraries/SDKs**: `openai` (GPT-4, GPT-4o, GPT-4o-mini), `psycopg2` (assumed for DB access), Chroma (vector DB), MinHash (set similarity), BM25 (text ranking).
   - **Models**: Fine-tuning with LoRA (rank=64, alpha=16, dropout=0.05, 4-bit precision) on 4x Nvidia 4090 GPUs; batch size=1, 1 epoch, lr=2e-4.
   - **Fine-tuning Time**: ~30 min (UQU), 4-5 hours (code generation).
   - **Code-Level Hints**:
     - Use MinHash + Jaccard for fast approximate set similarity on large databases.
     - Apply BM25 for keyword-based retrieval; exact match for purely numeric filters.
     - Fine-tune smaller models (Mistral-7B) for keyword extraction; larger models (GPT-4o-mini) for task decomposition.
     - Limit revision iterations (threshold=3 optimal for cost/accuracy balance; max=5 to prevent loops).
   - **Vector DB Config**: Chroma for entity storage; embedding dimensions depend on model (e.g., Stella-400M, text-embedding-3-large).

5. Evaluation & Performance:
   - **Metrics**: Execution Accuracy (EX) for SQL correctness; BLEU, ROUGE, GPT-4o score (calibrated with human eval) for task decomposition; F1 for keyword extraction.
   - **Benchmarks**: BIRD dev set (69.10% EX, up from 62.31% without fine-tuning); Spider dev (88.7%, from 84.2%).
   - **Performance Insights**:
     - UQU module contributes +9.18% accuracy gain (largest impact).
     - Entity retrieval adds +4.9%.
     - Revision improves accuracy but with cost tradeoff.
     - MinHash outperforms BM25 in speed/accuracy.
     - Smaller embedder (Stella-400M) surprisingly beats larger (Stella-1.5B).
   - **Scalability**: DeKeySQL achieves 52.4% runtime reduction vs. CHESS; 97% cost reduction (56.81s, $0.32 vs. 119.38s, $11).
   - **Error Analysis**: 49% of errors from evidence misalignment (17%), incorrect columns (11%), incorrect operations (8%).

6. Key Takeaways for System Design:
   - **Task-Specific Fine-Tuning**: Larger models excel at complex reasoning (task decomposition); smaller models sufficient for pattern matching (keyword extraction).
   - **Hybrid Retrieval is Essential**: Combine MinHash/BM25 for structured data, embeddings for unstructured; two-stage retrieval+re-ranking maximizes precision.
   - **Modular Design**: Separate UQU, retrieval, generation, and revision allows targeted optimization and debugging.
   - **Cost-Effective Revision**: Cap revision iterations (3-5) to balance accuracy and compute cost; avoid infinite loops.
   - **Dataset Quality > Size**: 1,500 high-quality annotated samples (DeKeyNLU) significantly boost performance; rigorous human verification crucial.
   - **Prompt Engineering**: Structure prompts with schema, tasks, entities, constraints, and ICL examples for stable SQL generation.
   - **Low-Level SDK Advantages**: Direct use of `openai`, `chroma`, MinHash, BM25 offers transparency, control, and cost efficiency vs. high-level frameworks.
   - **Calibration for LLM-as-Judge**: Align automated eval (GPT-4o scores) with human judgment via regression calibration for reliable metrics.

(Total ~498 words)
```
