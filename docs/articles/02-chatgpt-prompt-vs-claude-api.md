```
Paper Title: RAG-Fusion: a New Take on Retrieval-Augmented Generation

1. System Architecture:
   - RAG-Fusion extends traditional RAG with a multi-query generation + reciprocal rank fusion (RRF) pipeline
   - Pipeline flow: Original query → LLM generates multiple related queries → vector search on each query → RRF reranking → fused documents + queries sent to LLM for final answer
   - Modular design separates query expansion, retrieval, reranking, and generation stages
   - Traditional RAG: Query → Vector search → Top-n docs → LLM response
   - RAG-Fusion adds: Query diversification layer and RRF-based document fusion before final generation

2. Data Preparation & Processing:
   - Documents: Product datasheets, selection guides (PDFs) converted to text
   - Vector embeddings created from document text and stored in vector database (specific embedding model not mentioned)
   - Text chunking strategy not explicitly detailed, but retrieves n most relevant documents per generated query
   - Multimodal PDF handling noted as future work (tables, images from datasheets pose challenges)
   - No dimensionality reduction mentioned; relies on standard vector distance metrics for relevance ranking

3. Query Handling & Retrieval Logic:
   - **Query expansion**: Original query sent to LLM to generate 3-4 contextually diverse queries (e.g., "Tell me about MEMS microphones" → "What are MEMS microphones?", "What are advantages?", "Recommended products?")
   - Each generated query performs independent vector search retrieving n documents
   - **RRF scoring**: Each document gets score = 1/(rank + k), where rank is position in retrieval list, k is smoothing constant (typically 60)
   - Scores accumulated across all query results; documents fused and reranked by total RRF score
   - Final prompt includes: original query + generated queries + top reranked documents

4. Implementation Details:
   - Libraries: OpenAI API for LLM calls (likely GPT-3.5/4), vector database (unspecified, could be FAISS, Chroma, Pinecone)
   - Two LLM API calls: (1) generate queries from original, (2) generate final answer from queries + documents
   - RRF formula: `rrfscore = 1 / (rank + k)` where k is tunable (paper doesn't specify optimal k value)
   - Pseudocode-like flow: `queries = llm.generate_queries(original_query)` → `for q in queries: docs[q] = vector_search(q, top_n)` → `fused_docs = rrf_rerank(docs)` → `answer = llm.generate(original_query, queries, fused_docs)`
   - Performance bottleneck: Second LLM call (multiple queries + more documents = longer context) takes significantly more time (~1.77x slower than RAG)
   - Optimization hints: Host LLM locally to reduce API latency; reduce number of generated queries

5. Evaluation & Performance:
   - Runtime: RAG-Fusion averaged 34.62s vs. RAG 19.52s (1.77x slower) over 10 runs
   - Slowness attributed to second, more complex LLM call with expanded context
   - Evaluation: Manual assessment on accuracy, relevance, comprehensiveness (no automated metrics used effectively)
   - Traditional NLP metrics (ROUGE, BLEU) ineffective for open-ended sales/customer answers
   - New frameworks mentioned: RAGElo (tournament-style Elo ranking), Ragas (context precision, faithfulness, relevancy) — not yet tuned for this use case
   - Key finding: RAG-Fusion provides more comprehensive answers due to multi-perspective query generation but occasionally strays off-topic if generated queries diverge from original intent

6. Key Takeaways for System Design:
   - **Query diversification improves comprehensiveness**: Generate 3-4 related queries to cover multiple angles (technical specs, use cases, comparisons)
   - **RRF is simple and effective**: Easy to implement reranking without ML models; tune k constant (start with 60)
   - **Prompt engineering critical**: Users or system must ensure queries are clear to avoid irrelevant generated queries
   - **Trade-off latency for quality**: Accept ~2x slower responses for richer, multi-perspective answers
   - **Hybrid retrieval fusion**: RRF elegantly combines results from multiple query vectors without complex score normalization
   - **Context window management**: Passing multiple queries + more documents increases LLM input size; monitor token limits
   - **Weak at negatives**: Like RAG, struggles to give firm "no" answers when info absent from docs
   - **Low-level implementation**: Use `openai` SDK for LLM, `faiss`/`chromadb` for vector store, custom RRF in Python (`sorted()` + scoring loop)
   - **Caching opportunity**: Cache generated queries for repeated similar questions to reduce first LLM call overhead

(Total: ~500 words)
```