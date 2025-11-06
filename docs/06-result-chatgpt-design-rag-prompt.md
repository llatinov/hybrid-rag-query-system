
# Designing a RAG System Without a Vector Database

You can build a **Retrieval-Augmented Generation (RAG)** system *without* a dedicated vector database by relying on in-memory embeddings and cosine similarity search.

---

## 1. How to Create Embeddings

You can use OpenAI’s embedding models or open-source models from Sentence Transformers.

### Using OpenAI API
```python
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding
```

### Using Sentence Transformers
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    return model.encode(text)
```

---

## 2. Optimal Chunk Size

- **Chunk size**: ~500–1000 tokens (≈ 400–800 words)  
- **Overlap**: 100–200 tokens between chunks  

Example chunking function:

```python
def chunk_text(text, chunk_size=800, overlap=150):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks
```

---

## 3. Storage Strategy

✅ **Recommended**: Store all embeddings in **one dataset**, with metadata such as article ID or title.

Example structure:

```python
[
  {
    "article_id": "article_001",
    "chunk_id": 1,
    "text": "chunk text here...",
    "embedding": [0.12, 0.43, ...]
  },
  ...
]
```

This can be stored as JSON, CSV, or pickle.  
If your dataset is huge, you can store it per article.

---

## 4. End-to-End Example

Here’s a full working example using **Sentence Transformers**:

```python
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json

# --- Load model ---
model = SentenceTransformer('all-MiniLM-L6-v2')

# --- Step 1: Chunk and embed articles ---
def chunk_text(text, chunk_size=800, overlap=150):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def build_index(articles):
    index = []
    for article_id, text in articles.items():
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            embedding = model.encode(chunk)
            index.append({
                "article_id": article_id,
                "chunk_id": i,
                "text": chunk,
                "embedding": embedding.tolist()
            })
    return index

# Example data
articles = {
    "article_001": "Artificial intelligence is transforming industries...",
    "article_002": "Climate change impacts include rising sea levels..."
}

index = build_index(articles)

# Optional: Save to JSON
with open("embeddings_index.json", "w") as f:
    json.dump(index, f)

# --- Step 2: Search function ---
def search(query, index, top_k=3):
    query_embedding = model.encode(query)
    embeddings = np.array([item["embedding"] for item in index])
    sims = cosine_similarity([query_embedding], embeddings)[0]
    top_indices = sims.argsort()[-top_k:][::-1]
    results = [(index[i]["text"], sims[i], index[i]["article_id"]) for i in top_indices]
    return results

# --- Step 3: Example query ---
query = "How does AI affect business productivity?"
results = search(query, index)

for text, score, article_id in results:
    print(f"[{article_id}] score={score:.3f}\n{text[:200]}...\n")
```

---

## 5. RAG Prompt Example

```python
def build_prompt(question, retrieved_chunks):
    context = "\n\n".join(retrieved_chunks)
    return f"""
    You are an AI assistant. Use the following context to answer the question.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
```

---

### 🔍 Pipeline Summary

1. **Preprocessing** → Chunk → Embed → Save  
2. **Query time** → Embed query → Compute similarity → Retrieve top chunks  
3. **Augmentation** → Send chunks + query to your LLM

---

**You now have a complete RAG foundation without a vector database!**
