# Research Paper Analysis Prompt for Hybrid QA System

## Purpose
This prompt is designed to extract *practical and implementation-relevant* insights from research papers to inform the design and development of a **hybrid question-answering system**.  
The system should combine structured SQL query retrieval with unstructured text vector search, without using advanced frameworks (e.g., LangChain, LlamaIndex).  
Only low-level SDKs (like `openai`, `faiss`, `chromadb`, `sqlite3`, `psycopg2`) should be used.

---

## 🔍 Prompt for Each Research Paper

**Goal:** Extract practical, system-relevant insights to help design and implement a hybrid question-answering system that:
- Queries structured data through SQL.
- Retrieves unstructured text via vector search or embeddings.
- Does **not** rely on high-level frameworks (e.g., LangChain, LlamaIndex).
- Uses **low-level SDKs** and Python libraries directly (e.g., `openai`, `faiss`, `chromadb`, `sqlite3`, `psycopg2`, `pandas`, `numpy`, `scikit-learn`, etc.).

---

### 🧠 Prompt

> You are a senior data scientist and engineer analyzing this research paper to extract only the *practical implementation and system design insights* relevant to building a **hybrid question-answering system** that:
> - Queries structured data through SQL.
> - Retrieves unstructured text via vector search or embeddings.
> - Does **not** rely on high-level frameworks (e.g., LangChain, LlamaIndex).
> - Uses **low-level SDKs** and Python libraries directly (e.g., `openai`, `faiss`, `chromadb`, `sqlite3`, `psycopg2`, `pandas`, `numpy`, `scikit-learn`, etc.).
>
> Analyze the paper and summarize in **≤ 500 words**, focusing strictly on *practical and technical aspects* useful for implementation.
>
> Specifically extract and summarize:
>
> 1. **System Architecture:**
>    - Proposed or implied architecture patterns (e.g., pipelines, modular design, query routing, hybrid retrieval).
>    - Data flow between SQL and text retrieval components.
>
> 2. **Data Preparation & Processing:**
>    - Methods for cleaning, normalizing, or transforming text and tabular data.
>    - Embedding generation techniques (model types, preprocessing, chunking strategies, dimensionality reduction).
>    - Indexing and storage structures (e.g., FAISS, Chroma, custom ANN).
>
> 3. **Query Handling & Retrieval Logic:**
>    - How queries are parsed, classified, or routed to structured vs unstructured sources.
>    - Ranking, scoring, or hybrid retrieval fusion techniques.
>    - Any prompt-engineering or response-synthesis methods used.
>
> 4. **Implementation Details:**
>    - Libraries, APIs, or SDKs mentioned or suitable for adaptation.
>    - Code-level hints or pseudocode-like methods.
>    - Model selection, embedding dimensions, vector DB configurations, and performance optimization ideas.
>
> 5. **Evaluation & Performance:**
>    - Metrics, benchmarks, or experiments relevant to accuracy, latency, or cost-efficiency.
>    - Lessons learned for scaling, batching, or caching queries.
>
> 6. **Key Takeaways for System Design:**
>    - Concrete, actionable insights or best practices from this paper that can directly inform the hybrid QA system implementation.
>
> **Output Format (strictly):**
> ```
> Paper Title: [Insert title here]
> 
> 1. System Architecture:
>    - ...
> 
> 2. Data Preparation & Processing:
>    - ...
> 
> 3. Query Handling & Retrieval Logic:
>    - ...
> 
> 4. Implementation Details:
>    - ...
> 
> 5. Evaluation & Performance:
>    - ...
> 
> 6. Key Takeaways for System Design:
>    - ...
> 
> (Total ~500 words)
> ```

---

## ✅ Usage Recommendation
Apply this prompt iteratively to each research paper. You can automate it via the OpenAI API or manually use it within a chat session.
