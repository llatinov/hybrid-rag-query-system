# Research papers

## Core Papers on Hybrid Query Systems

1. ["Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"](https://arxiv.org/pdf/2005.11401)

Summary: This foundational paper introduces RAG as a general-purpose fine-tuning approach that combines pre-trained parametric memory (seq2seq models) and non-parametric memory (dense vector index) for language generation. The authors demonstrate how RAG models marginalize latent documents with top-K approximation and achieve state-of-the-art results on knowledge-intensive tasks.

Relevance: Essential for understanding the fundamental architecture of RAG systems. While the paper uses pre-trained models, the core concepts of combining retrieval and generation components are directly applicable to your low-level implementation needs.

2. ["RAG-Fusion: A New Take on Retrieval-Augmented Generation"](https://arxiv.org/html/2402.03367)

Summary: This paper presents RAG-Fusion, which combines RAG with Reciprocal Rank Fusion (RRF) by generating multiple queries, reranking them with reciprocal scores, and fusing documents and scores. The system provides accurate and comprehensive answers by contextualizing queries from various perspectives.

Relevance: Directly relevant for implementing the fusion mechanism between SQL and vector search results. The RRF algorithm described can be implemented using basic SDKs without frameworks.

3. ["DeKeyNLU: Enhancing Natural Language to SQL Generation through Task Decomposition and Keyword Extraction"](https://arxiv.org/html/2509.14507)

Summary: This paper presents a dataset and methodology for refining task decomposition and enhancing keyword extraction precision for NL2SQL pipelines. The DeKeySQL system employs three distinct modules for user question understanding, entity retrieval, and generation, improving SQL generation accuracy on BIRD (62.31% to 69.10%) and Spider (84.2% to 88.7%) datasets.

Relevance: Highly relevant for the query decomposition component of your system, providing practical approaches for breaking down complex natural language queries into SQL-executable components.

## Papers on Query Decomposition and Understanding

4. ["Training Table Question Answering via SQL Query Decomposition"](https://arxiv.org/html/2402.13288)

Summary: This paper shows how learning to imitate SQL-like algebraic operations provides intermediate supervision steps that allow increased generalization and structural reasoning. The execution flow of SQL operations provides a framework for systematic query decomposition.

Relevance: Provides insights into decomposing complex queries into manageable sub-queries that can be processed independently - crucial for your system's query understanding module.

5. ["Framework for Developing Natural Language to SQL (NL to SQL) Technology"](https://promptengineering.org/framework-for-developing-natural-language-to-sql-nl-to-sql-technology/)

Summary: This framework paper describes decomposition algorithms for breaking down complex queries into manageable sub-queries, using dense vector search to retrieve relevant tables and columns, and processing sub-queries individually before integrating results.

Relevance: Offers practical implementation guidance for building NL2SQL systems from fundamental components, aligning perfectly with your no-framework requirement.

## Papers on Hybrid Search and Result Fusion

6. ["Reciprocal Rank Fusion (RRF) explained in 4 mins — How to score results form multiple retrieval methods in RAG"](https://medium.com/@devalshah1619/mathematical-intuition-behind-reciprocal-rank-fusion-rrf-explained-in-2-mins-002df0cc5e2a) / ["Relevance scoring in hybrid search using Reciprocal Rank Fusion (RRF)"](https://learn.microsoft.com/en-us/azure/search/hybrid-search-ranking)

Summary: The original RRF paper demonstrates how the algorithm evaluates search scores from multiple ranked results using the formula 1/(rank + k), where k is typically set to 60. RRF effectively combines evidence from multiple sources without requiring score normalization.

Relevance: Critical for implementing the fusion mechanism between SQL and vector search results. The algorithm is simple enough to implement directly without frameworks.

7. ["HybridRAG: Integrating Knowledge Graphs and Vector Retrieval Augmented Generation for Efficient Information Extraction"](https://arxiv.org/html/2408.04948v1)

Summary: This paper presents a combination of GraphRAG and VectorRAG techniques for enhanced Q&A systems, demonstrating how to integrate retrieval mechanisms from both structured and unstructured data sources without relying on complex frameworks.

Relevance: Provides architectural patterns for combining structured (SQL-like) and unstructured (vector) data retrieval, which is exactly what your system needs to accomplish.

## Papers on Building Systems Without Frameworks

8. ["A beginner's guide to building a Retrieval Augmented Generation (RAG) application from scratch"](https://learnbybuilding.ai/tutorial/rag-from-scratch/)

Summary: This practical guide demonstrates building RAG systems without libraries or frameworks, showing that the essence of RAG involves adding retrieval data to prompts passed to LLMs, with implementations possible in as few as five lines of code.

Relevance: Directly addresses your requirement of building without frameworks, providing practical code examples and architectural guidance for low-level implementation.

9. ["RAG-based Question Answering over Heterogeneous Data and Text"](https://arxiv.org/html/2412.07420)

Summary: This paper addresses QA systems operating over heterogeneous sources including text, knowledge graphs, and tables. It demonstrates how to combine multiple pieces of evidence of different modalities without complex frameworks.

Relevance: Highly relevant for handling both structured (SQL) and unstructured (text/vector) data sources in a unified system.

## Papers on Answer Synthesis and Multi-Source Integration

10. ["ER-RAG: Enhance RAG with ER-Based Unified Modeling of Heterogeneous Data Sources"](https://arxiv.org/html/2504.06271)

Summary: This framework enables RAG systems to integrate information from multiple heterogeneous data sources through a two-stage process: source selection and API chain construction. The system leverages schema information for precise and context-aware generation.

Relevance: Provides architectural patterns for synthesizing answers from multiple data sources (SQL and vector), which is essential for your final answer generation component.

11. ["ASKSQL: Enabling cost-effective natural language to SQL conversion for enhanced analytics and search"](https://www.sciencedirect.com/science/article/pii/S2666827025000246)

Summary: This paper presents an end-to-end NL2SQL pipeline that integrates optimized query recommendation, entity-swapping, and skeleton-based caching. It includes an intelligent schema selector for handling large schemas and a fast adapter-based query generator.

Relevance: Offers practical optimization techniques for SQL generation that can be implemented using low-level SDKs, particularly useful for the SQL query construction component.

## Implementation-Focused Resources

12. ["Building a Production-Ready RAG System from Scratch: An Architectural Deep Dive"](https://blog.4geeks.io/building-a-production-ready-rag-system-from-scratch-an-architectural-deep-dive/)

Summary: This comprehensive guide bypasses high-level frameworks to expose core mechanics, implementing systems using Python with PostgreSQL/pgvector for vector search and OpenAI API, focusing on architectural decisions and performance trade-offs.

Relevance: Provides production-ready code examples and architectural patterns specifically for building without frameworks, using only low-level SDKs.

## Why These Papers Are Most Relevant

These papers collectively address all aspects of your requirements:

1. Query Understanding & Decomposition: Papers 3, 4, 5, and 11 provide concrete algorithms for breaking down natural language queries into structured components suitable for both SQL and vector search.
2. Data Retrieval Without Frameworks: Papers 8 and 12 specifically demonstrate building systems using only low-level SDKs like OpenAI's library, avoiding LangChain/LlamaIndex.
3. Result Combination: Papers 2 and 6 provide the mathematical foundation and practical implementation of RRF for combining results from different sources without complex normalization.
4. Answer Synthesis: Papers 9, 10, and 1 show how to synthesize coherent answers from heterogeneous data sources, crucial for your final output generation.
5. System Architecture: Papers 7 and 10 provide architectural patterns for integrating SQL and vector search components in a unified system.

These papers provide both theoretical foundations and practical implementation guidance, making them ideal references for building your hybrid query system from scratch using only low-level SDKs.
