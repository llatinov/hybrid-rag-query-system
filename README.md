# Hybrid RAG Query System

## Information

A system that answers user questions by querying both a structured database (SQL) and an unstructured text corpus (via vector search). The solution uses OpenAI SDK library directly.

## Requirements

1. **Input:** The system accepts a natural language question from the user.
2. **Outputs:** The system synthesizes the information and generates a coherent, natural language answer to the user's original question.

## Implementation steps

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
