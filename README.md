# Hybrid RAG Query System

## Information

A system that answers user questions by querying both a structured database (SQL) and an unstructured text corpus (via vector search). The solution uses OpenAI SDK library directly. The solution does not use vector database. Embeddings and vector search is handled in the code.

## Requirements

1. **Input:** The system accepts a natural language question from the user.
2. **Outputs:** The system synthesizes the information and generates a coherent, natural language answer to the user's original question.

## Usage

1. Set OpenAI API key: `export OPENAI_API_KEY='your_api_key_here'`
2. Enable SQL search debug for more details: `export SQL_SEARCH_DEBUG=true`
3. Enable text search debug for more details: `export TEXT_SEARCH_DEBUG=true`
4. Run the application: `python app.py`

## Data

- [Northwind-SQLite3](https://github.com/jpwhite3/northwind-SQLite3) - an excellent tutorial schema for a small-business ERP, with customers, orders, inventory, purchasing, suppliers, shipping, employees, and single-entry accounting.
- [MAVEN-dataset](https://github.com/THU-KEG/MAVEN-dataset) - Source code and dataset for EMNLP 2020 paper "MAVEN: A Massive General Domain Event Detection Dataset".

## Implementation notes

- NL2SQL seems to be very tough field with ongoing research, nevertheless OpenAI works fairly well with Northwind.
- Even without the schema provided OpenAI returns good suggestions for simple queries? Is BIRD-bench included in OpenAI knowledge?
- Chunk by length produces 907 chunks, chunk by sentences produces more than three times - 3061, very inefficient. Will revert after play with it?

### Data preparation

- Northwind database is processed on application initialization if needed
- SQL schema is created and OpenAI API is called to describe the SQL schema
- The resulting metadata and save this to a JSON file conforming to predefined with JSON schema

- MAVEN is processed on application initialization if needed
- Articles are glued together fro the original individual sentences
- There are tow experiments here to see which chunking is better:
  - Each article is split into sentences, which are combined into a chunk not longer than 512 characters and with one sentence overlap
  - Each article is split by word count on 512 characters with 50 characters overlap
- Embedding are generated for each text chunk with OpenAI embeddings API
- The results are saved into a CSV file to be used later with Pandas and NumPy to do the searching

## Implementation steps

More details available in `implementation-steps.md`, here is only high-level overview.

1. Find research articles - Find several research papers that match the systems requirements using Claude's Opus 4.1.
2. Comprehend the articles - Read and understand the articles. Here I went in a deep rabbit hole, trying to summarize the articles with LLM API calls.
3. Extract valuable info from articles - Extract ideas and terms from the articles that can eb researched later.
4. Prepare SQL data and metadata - Find a test database and generate its metadata.
5. Ask question on the SQL data - Using the metadata generate SQL queries based on user's question. Run the queries and pass the results so OpenAI can answer the question.
6. Prepare text data and its embeddings - Find a test set of articles, chunk them, generate embeddings with OpenAI and save to file
7. Search text data - Process user input through OpenAI API, generating several versions of it, which are used in semantic search and keywords, which are used in full text search.

## TODO

- (Optimization) Tables metadata is extracted out of the full schema metadata in order to reduce the context window
- (Optimization) Split the tables data into smaller files and make tables metadata to refer to those files, this is for further optimization of the context
- (Security) Mechanism to check if user has access to the SQL data
