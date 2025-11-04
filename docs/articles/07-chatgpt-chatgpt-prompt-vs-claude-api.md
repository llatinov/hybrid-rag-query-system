```
Paper Title: HybridRAG: Integrating Knowledge Graphs and Vector Retrieval Augmented Generation for Efficient Information Extraction

1. System Architecture:
   - **Modular Pipeline Design**: The paper proposes a three-tier architecture comparing VectorRAG, GraphRAG, and HybridRAG. VectorRAG uses embeddings + vector database retrieval, GraphRAG uses knowledge graph (KG) triplet extraction and graph traversal, and HybridRAG concatenates contexts from both for unified LLM input.
   - **Data Flow**: Documents → chunking (1024 chars, no overlap) → parallel paths: (a) embeddings → Pinecone vector DB, (b) LLM-based triplet extraction → NetworkX graph. Query triggers retrieval from both, contexts merged, then sent to GPT-3.5-turbo for answer generation.
   - **Metadata Filtering**: Both pipelines explicitly filter by company name, quarter, and year metadata to ensure retrieval relevance.

2. Data Preparation & Processing:
   - **Document Ingestion**: PyPDFLoader used for PDF parsing; RecursiveCharacterTextSplitter with chunk size 1024, overlap 204 for VectorRAG preprocessing.
   - **Embeddings**: OpenAI's text-embedding-ada-002 model generates vector representations for semantic similarity search in Pinecone.
   - **KG Construction**: Two-stage LLM prompting: (1) generate abstract/refined chunk summaries, (2) extract entity-relation triplets [head, type, relation, object, type, metadata]. Entities include companies, financial metrics, executives, products, locations, events, legal info.
   - **Entity Disambiguation**: Coreference resolution links mentions (e.g., "the company" and "it") to same entity node; concise entity names (<4 words preferred).
   - **Storage**: Triplets stored in pickle files; Pinecone for vectors; NetworkX for graph manipulation.

3. Query Handling & Retrieval Logic:
   - **VectorRAG Retrieval**: Query embedded, top-k (k=4) similar chunks retrieved via cosine similarity from Pinecone after filtering by metadata (20 candidates considered).
   - **GraphRAG Retrieval**: Query triggers depth-first search (DFS depth=1) from relevant entities in KG; subgraph extracted with nodes/edges as context.
   - **HybridRAG Fusion**: Contexts from VectorRAG appended first, then GraphRAG context concatenated. No re-ranking or weighted fusion; simple concatenation.
   - **Prompt Engineering**: Custom prompts instruct GPT-3.5-turbo to act as expert Q&A system, use only provided context, avoid explicit context references.

4. Implementation Details:
   - **Libraries/SDKs**: LangChain (RetrievalQA, GraphQAChain), Pinecone (vector DB), NetworkX (graph ops), OpenAI API (GPT-3.5-turbo, text-embedding-ada-002), PyPDFLoader, pickle for serialization.
   - **Configuration**: LLM temperature=0 (deterministic), max output tokens=1024, chunk size=1024, no overlap. KG: 13,950 triplets, 11,405 nodes, 13,883 edges across 50 financial documents.
   - **No High-Level Frameworks**: Though LangChain is mentioned, core logic (embedding, graph traversal, context merging) can be replicated with low-level SDKs (openai, faiss/chromadb, networkx, pandas).
   - **Scalability**: Parameterized by company/quarter/year for easy dataset expansion; iterative processing of questions from CSV; outputs stored as CSV/JSON.

5. Evaluation & Performance:
   - **Metrics**: Faithfulness (F), Answer Relevance (AR), Context Precision (CP), Context Recall (CR) using RAGAS framework adapted with LLM-based verification.
   - **Results**: HybridRAG excels in F (0.96), AR (0.96), CR (1.0); GraphRAG best in CP (0.96); VectorRAG lags in F (0.94) and CP (0.84). HybridRAG's lower CP (0.79) is due to concatenated contexts introducing noise.
   - **Trade-offs**: GraphRAG better for extractive Qs with explicit entities; VectorRAG better for abstractive Qs; HybridRAG balances both, acting as fallback mechanism.
   - **Dataset**: 400 Q&A pairs from 50 Nifty-50 earnings call transcripts (avg 27 pages, 60k tokens, 16 Qs each).

6. Key Takeaways for System Design:
   - **Hybrid retrieval is superior**: Combining vector similarity and graph traversal improves robustness across query types (extractive vs. abstractive).
   - **Metadata is critical**: Explicit filtering by metadata (company, date) boosts precision in both VectorRAG and GraphRAG.
   - **Two-stage KG construction works**: LLM-based summarization + triplet extraction via prompt engineering is practical without specialized NER/RE models.
   - **Simple fusion suffices**: Concatenating contexts from both retrievers outperforms either alone; no complex re-ranking needed initially.
   - **DFS depth=1 for graphs**: Shallow graph traversal balances context richness and noise; deeper traversal may degrade precision.
   - **Chunk size matters**: 1024-char chunks with no overlap work well for financial docs; avoid oversized chunks that lose granularity.
   - **Implementation path**: Use openai SDK for embeddings/LLM, faiss/chromadb for vector store, networkx for KG, psycopg2/sqlite3 for metadata, pandas for I/O, and numpy/scikit-learn for similarity calculations.

(Total ~498 words)
```