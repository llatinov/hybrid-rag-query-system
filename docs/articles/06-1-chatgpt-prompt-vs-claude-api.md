```
Paper Title: Reciprocal Rank Fusion (RRF) explained in 4 mins — How to score results from multiple retrieval methods in RAG

1. System Architecture:
   - **Hybrid Retrieval Pipeline**: RRF operates as a rank aggregation layer that sits between multiple retrieval systems and the generation component in RAG architectures.
   - **Multi-Retriever Pattern**: The system employs parallel retrievers (e.g., BM25 for keyword-based sparse retrieval, dense embedding models for semantic search) that independently rank documents.
   - **Data Flow**: User query → Multiple retrievers (parallel execution) → Individual rankings → RRF fusion layer → Unified ranking → Top-k selection → Generative model.
   - **Modular Design**: Each retriever operates independently, making the system extensible and allowing easy addition/removal of retrieval methods without architectural changes.

2. Data Preparation & Processing:
   - **Dual Indexing Strategy**: Maintain separate indexes for different retrieval methods (e.g., inverted index for BM25, vector index for dense retrieval using FAISS or ChromaDB).
   - **No Special Preprocessing for RRF**: RRF operates on rank positions only, not raw scores, eliminating the need for score normalization across heterogeneous retrievers.
   - **Document Representation**: Documents should be indexed in both sparse (term-based) and dense (embedding-based) formats to support multiple retrieval paradigms.

3. Query Handling & Retrieval Logic:
   - **Core RRF Formula**: `RRF(d) = Σ(r ∈ R) 1/(k + r(d))` where d is a document, R is the set of rankers, k is a constant (typically 60), and r(d) is the rank of document d in ranker r.
   - **Scoring Mechanism**: Uses reciprocal ranking to weight higher-ranked documents more heavily while providing diminishing returns for lower ranks.
   - **No Query Routing**: Unlike router-based systems, RRF queries all retrievers simultaneously, making it simpler to implement.
   - **Fusion Strategy**: Aggregates evidence by summing reciprocal ranks across all retrievers, naturally handling cases where documents appear in some but not all rankings.

4. Implementation Details:
   - **Simple Python Implementation**:
     ```python
     def calculateRRF(rankings, k=60):
         scores = {}
         for ranker_results in rankings:
             for rank, doc_id in enumerate(ranker_results, start=1):
                 scores[doc_id] = scores.get(doc_id, 0) + 1/(k + rank)
         return sorted(scores.items(), key=lambda x: x[1], reverse=True)
     ```
   - **SDKs and Libraries**: Use `rank_bm25` or custom BM25 implementation for sparse retrieval; `openai` or `sentence-transformers` for embeddings; `faiss` or `chromadb` for vector storage.
   - **k Parameter Tuning**: While k=60 is empirically optimal across many datasets, consider tuning between 40-80 based on retrieval depth and application requirements.
   - **No Training Required**: RRF is parameter-free (except k) and requires no machine learning training, making it immediately deployable.
   - **Handles Missing Documents**: Naturally assigns zero contribution if a document doesn't appear in a particular ranker's results.

5. Evaluation & Performance:
   - **Computational Efficiency**: O(n*r) complexity where n is number of documents and r is number of rankers - very lightweight compared to learned fusion methods.
   - **Robustness**: Empirically shown to outperform individual retrievers and simple score-based fusion methods by reducing sensitivity to retriever biases.
   - **Score Distribution**: Example reciprocal values: rank 1 ≈ 0.0164, rank 10 ≈ 0.0143, rank 100 ≈ 0.00625 (with k=60), demonstrating smooth decay.
   - **Latency Considerations**: Since retrievers run in parallel, total latency is max(retriever latencies) + minimal RRF computation overhead.

6. Key Takeaways for System Design:
   - **Simplicity is Key**: RRF provides strong performance without complex learned models, ideal for low-level SDK implementations.
   - **Implementation Priority**: Focus first on getting multiple quality retrievers (BM25 + dense embeddings) running correctly; RRF fusion adds 10-20 lines of code.
   - **Index Management**: Maintain separate indexes using `sqlite3`/`psycopg2` for metadata and `faiss`/`chromadb` for vectors; tie them together via document IDs.
   - **Parameter Tuning**: Start with k=60, but create a simple grid search over k values if optimizing for specific datasets.
   - **Scale Considerations**: RRF scales linearly with number of retrievers; typically 2-3 retrievers (keyword + 1-2 semantic) provide optimal cost-benefit tradeoff.
   - **Production Pattern**: Implement as a standalone fusion module that accepts List[List[doc_id]] and returns List[Tuple[doc_id, score]] for clean separation of concerns.

(Word count: ~495)
```