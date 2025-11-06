# Hybrid RAG Query System

# Implementation steps

### 1. Find research articles

Query Claude's Opus 4.1 to find research papers that match the systems requirements.

Prompts:

- docs/01-prompt-find-research-papers.md

Results:

- docs/01-result-claude-opus-research-papers.md

### 2. Comprehend the articles

In order to get a solution, the papers should be well understood. This is a mix of manually reading/scanning the papers + LLM summarization.
Automate the summarization part by generate LLM summarization prompts from both ChatGPT and Claude.
Generate python files which will run the prompts for each article, the Claude prompt will be run against ChatGPT and vice versa. Python files are manually polished.
Alongside with the python files, Claude code generated a summarization prompt, which seems to produce good results.

Processing errors:

- Article 01 could not be processed by ChatGPT because the result is binary file
- Article 04 could not be processed by Claude as it is too long
- Article 09 could not be processed by ChatGPT with gpt-5-nano as content is too big
- Article 10 could not be processed by ChatGPT/Claude as `requests` is not allowed to access the site

The summarization results are placed in **docs/articles** folder.

Observations:

- Claude is much more expensive: https://openai.com/api/pricing/ vs https://docs.claude.com/en/docs/about-claude/pricing
- Claude API constantly hits the token per minute limit, this is uncomfortable and not very practical

Prompts:

- docs/02-prompt-generate-research-paper-analysis-prompt.md
- docs/03-claude-code-generate-python-scripts.md

Results:

- docs/02-result-chatgpt-research-paper-analysis-prompt.md
- docs/02-result-claude-opus-research-paper-analysis-prompt.md
- docs/03-result-claude-code-process-articles-claude.py
- docs/03-result-claude-code-process-articles-openai.py
- docs/03-result-claude-code-prompt.md
- docs/articles/\*.md

### 3. Extract valuable info from articles

In general reviewing so many papers, even with LLM summary is tedious process. Papers are very abstract and lack implementation details.

The result is several techniques or terms that needs to be researched further for practical usage. Those are split into the general blocks of the application to be developed.

#### RAG Fusion on the textual data

- Acquire data (Wikidump? Or?)
- VectorDB: Vectorize it and save it into vector DB (FAISS/ChromaDB) or MIPS index using FAISS?
- Plain: We do similarity search with jaccard similarity? Use numpy for vector math over the text?
- Use LLM in one go to generate several search queries (3-5) from the user query (Is it better to generate search queries or search keywords?) - "generate 5 search queries with their corresponding probabilities, sampled from the full distribution"
- RRF: rrfscore = 1 / (rank + k) - use article 06 for more details
- Take first 5 or 10 results (how de we chunk the data?) and give it to the LLM to summarize
- Keep citations

#### Language to SQL and search the database

- Acquire SQL database with data
- NL2SQL - oh, boy, how do we do that, all papers (03, 04, 05 and 11) are abstract and do not give much details
- NL2SQL + TEXT2SQL - research more, find a library?
- BIRD dataset?
- MinHash/BM25 retrieves top-5 column names and table values
- MinHash + Jaccard Score for column names
- Embedding model + cosine similarity for top-5 descriptions
- Chain-of-Thought (CoT) prompts for task decomposition
- Search (vector + text) on database schema elements (table/column names, values, descriptions) to find a match
- RAG Fusion for better precision
- RAT-SQL
- GNN-based encoder
- ANN
- Break into main task and subtasks, iterate on those
- Add feedback loop to improve results
- Larger models excel at complex reasoning (task decomposition); smaller models sufficient for pattern matching (keyword extraction).
- Keep SQL results and visualize for feedback

#### Answer synthesis

- Take the text and SQL results and merge them into one answer?
- Provide two answers?
- Keep citations

### 4. Prepare SQL data and metadata

Find a test database and process it in order to generate its metadata, which will be used later for reasoning with the LLM.

### 5. Ask question on the SQL data

Pass the database metadata to OpenAI API in order to understand and map user query to a table and create SQL query. Execute the queries and get results.Pass results to LLM along with user question in order to answer user's query based on SQL results.

### 6. Prepare text data and its embeddings

Find a archive with articles and process the text to create articles chunks and embeddings. The hybrid RAG system will not use Vector DB, so vectorization and embeddings are handled in the code.

Prompts:

- docs/06-prompt-design-rag-prompt.md

Results:

- docs/06-result-chatgpt-design-rag-prompt.md
- docs/06-result-claude-opus-design-rag-prompt.md
