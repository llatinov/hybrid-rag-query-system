# ASKSQL Research Paper Analysis

## Practical Implementation Insights for Hybrid QA System

**Paper Title:** ASKSQL: Enabling cost-effective natural language to SQL conversion for enhanced analytics and search

---

## 1. System Architecture

- **End-to-end pipeline with modular components:** Semantic Similarity Module → Entity Swapping Module → Semantic Caching Module → Query Generator (Schema Selection + SQL Generation)
- **Hybrid approach** combining query recommendations from historical data with generative SQL capabilities
- **Fallback mechanism:** Uses cached/historical queries first, then falls back to generation if no match found
- **Three-tier processing:** similarity check against history → semantic caching with high threshold → new query generation
- **Query flow** uses ANN index for fast similarity search, entity-masked POS tagging for skeleton matching, and adapter-based fine-tuned PLMs for generation

## 2. Data Preparation & Processing

- **Custom-trained RoBERTa NER model** for entity recognition (organizations, locations, persons)
- **Entity masking** converts queries to skeleton format (e.g., "Apple Inc." → "ORG") for better pattern matching
- **Embedding generation** using FAISS for vector similarity with approximate nearest neighbor search
- **Schema filtering:** First uses vector embeddings to select top 16-32 tables, then RoBERTa-large classifier assigns probabilities
- **Syntactic dependency parsing** creates directed graphs for sentence pair matching using POS tags as node features

## 3. Query Handling & Retrieval Logic

- **ANN search** finds k-nearest query embeddings, then re-ranks using dot product similarity scores
- **Skeleton Aware-Association-Graph Network (SA-AGN)** for semantic caching using Quadratic Assignment Problem (QAP) to match subgraphs
- **Entity swapping** replaces tagged placeholders with actual values from NL queries (reduces need for regeneration)
- **Schema selection** uses combined probability scoring: P(table) × P(columns) for ranking relevant tables
- **Caching threshold** carefully tuned to reduce false positives while maintaining speed benefits

## 4. Implementation Details

- **FAISS library** for ANN index and fast similarity computations
- **8-bit quantization using QLoRA** for CodeLlama-13b model (reduces memory from 15.6GB to 4.68GB)
- **Custom NER with CRF layer** using Viterbi algorithm for sequence labeling
- **BiLSTM replaced** with hyphenated column names to reduce token count (e.g., "employee id" → "employee-id")
- **Training parameters:** learning rate 4e-3, batch size 8, 16 epochs, max sequence 700 tokens, weight decay 0.001
- **Infrastructure:** Tesla A100 40GB GPU for experiments, average latency 4.6s for quantized 13b model

## 5. Evaluation & Performance

- **32.6% latency reduction** and **5.83% accuracy improvement** with increased usage
- **CodeLlama-13b-quantized** achieves 82.38% execution accuracy on enterprise data
- **Cost reduced to $0.000045 per query** (vs $0.0377 for GPT-4 based systems)
- **Memory usage** reduced to 4.68GB with quantization vs 15.6GB original
- **Semantic caching alone** provides 2.175% accuracy boost while reducing response time by 0.43s
- **Pipeline tested** on 4887 training and 1214 test enterprise samples with 62% standard queries

## 6. Key Takeaways for System Design

- **Combine fast similarity search** (FAISS/ANN) with robust semantic matching (graph-based QAP) for dual-layer caching
- **Entity masking and swapping** dramatically reduces LLM calls for similar queries with different entities
- **Quantization (8-bit)** provides 70% memory reduction with minimal accuracy loss (~1.5%)
- **Pre-filter schemas** using embeddings before classification to handle large schema spaces efficiently
- **Small domain-specific fine-tuned models** can outperform large general models for specialized SQL generation
- **Adaptive threshold tuning** for semantic caching critical to balance speed vs accuracy tradeoff

---

## Summary

The ASKSQL paper presents a production-ready hybrid QA system that achieves significant cost and latency reductions while maintaining competitive accuracy. The key innovation lies in its multi-tiered caching strategy combined with entity swapping and quantized models, making it particularly suitable for enterprise environments with repetitive query patterns. The use of low-level SDKs (FAISS, custom NER, quantized PLMs) aligns perfectly with the requirement to avoid high-level frameworks while building an efficient NL2SQL system.
