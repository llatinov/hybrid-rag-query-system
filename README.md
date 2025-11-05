# Hybrid RAG Query System

## Information

A system that answers user questions by querying both a structured database (SQL) and an unstructured text corpus (via vector search). The solution uses OpenAI SDK library directly.

## Requirements

1. **Input:** The system accepts a natural language question from the user.
2. **Outputs:** The system synthesizes the information and generates a coherent, natural language answer to the user's original question.

## Usage

1. Set OpenAI API key: `export OPENAI_API_KEY='your_api_key_here'`
2. Disable SQL debug if output is too much: `export SQL_DEBUG=false`
3. Run the query assistant: `python data/query_assistant.py`

## Data

- [Northwind-SQLite3](https://github.com/jpwhite3/northwind-SQLite3) - an excellent tutorial schema for a small-business ERP, with customers, orders, inventory, purchasing, suppliers, shipping, employees, and single-entry accounting.

## Implementation details

Explain your design choices, the logic for query understanding and decomposition, data retrieval, result combination, and answer synthesis.
Explain the challenges you encountered while building this system from scratch, particularly in the absence of high-level frameworks.

Notes:

- NL2SQL seems to be very tough field with ongoing research, nevertheless OpenAI works fairly well with Northwind.
- Even without the schema provided OpenAI returns good suggestions for simple queries? Is BIRD-bench included in OpenAI knowledge?

### Data preparation

- Northwind database is processed on application initialization
- SQL schema is created and OpenAI API is called to describe the SQL schema
- The resulting metadata and save this to a JSON file conforming to predefined with JSON schema

## Implementation steps

More details available in `implementation-steps.md`, here is only high-level overview.

1. Find research articles - Find several research papers that match the systems requirements using Claude's Opus 4.1.
2. Comprehend the articles - Read and understand the articles. Here I went in a deep rabbit hole, trying to summarize the articles with LLM API calls.
3. Extract valuable info from articles - Extract ideas and terms from the articles that can eb researched later.
4. Prepare SQL data and metadata - Find a test database and generate its metadata.
5. Ask question on the SQL data - Using the metadata generate SQL queries based on user's question. Run the queries and pass the results so OpenAI can answer the question.

## TODO

- (Optimization) Tables metadata is extracted out of the full schema metadata in order to reduce the context window
- (Optimization) Split the tables data into smaller files and make tables metadata to refer to those files, this is for further optimization of the context
- (Security) Mechanism to check if user has access to the data
