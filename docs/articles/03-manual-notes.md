# Summary

["DeKeyNLU: Enhancing Natural Language to SQL Generation through Task Decomposition and Keyword Extraction"](https://arxiv.org/html/2509.14507)

Article presents DeKeySQL dataset that helps from NLP2SQL conversion. It does not specify precisely how to do it.
**Research NLP2SQL methods?**
**Research Chain-of-Thought (CoT) reasoning?**

## 3.1 Data Sources

BIRD contains 12,751 text-to-SQL pairs across 95 databases (33.4 GB), spanning 37 professional domains, and is specifically designed for evaluating and training NL2SQL models.

Takeaways:
Larger models excel at complex reasoning (task decomposition); smaller models sufficient for pattern matching (keyword extraction).
User question → UQU (task decomposition + keyword extraction) → Entity Retrieval (database matching) → Generation (SQL creation) → Revision (error correction) → Final SQL execution.
MinHash/BM25 retrieves top-5 column names and table values (score > 0); re-ranker selects top-2.
