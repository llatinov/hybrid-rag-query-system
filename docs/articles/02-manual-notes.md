# Summary

["RAG-Fusion: A New Take on Retrieval-Augmented Generation"](https://arxiv.org/html/2402.03367)

RAG-Fusion method, the article is a bit bloated, not really relevant to the assignment, could improve it though.

## Introduction

It has been found that reranking in retrieval-augmented generation plays a significant role in improving retrieval results
It has been found that RRF outperforms many other document reranking methods

## RAG vs RAG-Fusion

Create vector embeddings – numerical representations of the text that the algorithm can understand – and store them in a vector database.
**How to do this in my case, without vector database, directly search into the text? MIPS index using FAISS from 01?**

RAG-Fusion has a few extra steps. Once the original query is received, the model sends the original query to the large language model to generate a number of new search queries based on the original query.
**Use the "generate 5 search queries with their corresponding probabilities, sampled from the full distribution"?**
**Do we generate search queried of keywords in RAG?**

Then perform RRF (reciprocal rank fusion) rrfscore = 1 / (rank + k), rank of the documents sorted by distance, and k is a constant smoothing factor that determines the weight given to the existing ranks. Upon each calculation of the score, the rrf score is accumulated with previous scores for the same document, and when all scores are accumulated, documents are fused together and reranked according to their scores.
**Understand better the formula here and how to apply in practice?**

## LLM article review

FAISS, Chroma, Pinecone - vector databases
