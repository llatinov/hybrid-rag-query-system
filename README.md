# Hybrid RAG Query System

## Information

A system that answers user questions by querying both a structured database (SQL) and an unstructured text corpus (via vector search).

## Requirements

1. **Input:** The system accepts a natural language question from the user.
2. **Outputs:** The system synthesizes the information and generates a coherent, natural language answer to the user's original question.

## Implementation steps

1. Query Claude's Opus 4.1 to find research papers that match the systems requirements. Result papers are listed in **docs/research-papers.md**
