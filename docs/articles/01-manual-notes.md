# Summary

["Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"](https://arxiv.org/pdf/2005.11401)

Article is old, might not be very relevant.

## 1 Introduction

the parametric memory is a pre-trained seq2seq transformer, and the non-parametric memory is a dense vector index of Wikipedia, accessed with a pre-trained neural retriever
**How to do this? Research a bit more.**

## 3 Experiments

Each Wikipedia article is split into disjoint 100-word chunks, to make a total of 21M documents. We use the document encoder to compute an embedding for each document, and build a single MIPS index using FAISS.
**What is MIPS index using FAISS?**

## Effect of Retrieving more documents

Models are trained with either 5 or 10 retrieved latent documents, and we do not observe significant differences in performance between them.
performance peaks for RAG-Token at 10 retrieved documents
**Use 10 as result size?**
