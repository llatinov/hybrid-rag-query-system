"""
Process article URLs with Claude API.

This script:
1. Reads a map of article URLs (key:value pairs)
2. Loads a prompt from prompt.md
3. For each article, fetches the content via HTTP and adds it to the prompt
4. Calls Claude API with the combined prompt + article content
5. Saves each response to a file named <key>-claude.md
"""

import os
from anthropic import Anthropic
from pathlib import Path
import requests


# Configuration
MODEL = "claude-sonnet-4-5-20250929"  # or "claude-3-5-sonnet-20241022", "claude-3-opus-20240229", etc.
OUTPUT_DIR = "articles"

# Map of article URLs to process (key: identifier, value: URL)
ARTICLE_URLS = {
    # "01": "https://arxiv.org/pdf/2005.11401",  # too old, no HTML version, skip for now
    "02": "https://arxiv.org/html/2402.03367",
    "03": "https://arxiv.org/html/2509.14507",
    "04": "https://arxiv.org/html/2402.13288",
    "05": "https://promptengineering.org/framework-for-developing-natural-language-to-sql-nl-to-sql-technology/",
    "06-1": "https://medium.com/@devalshah1619/mathematical-intuition-behind-reciprocal-rank-fusion-rrf-explained-in-2-mins-002df0cc5e2a",
    "06-2": "https://learn.microsoft.com/en-us/azure/search/hybrid-search-ranking",
    "07": "https://arxiv.org/html/2408.04948v1",
    "08": "https://learnbybuilding.ai/tutorial/rag-from-scratch/",
    "09": "https://arxiv.org/html/2412.07420",
    "10": "https://arxiv.org/html/2504.06271",
    "11": "https://www.sciencedirect.com/science/article/pii/S2666827025000246",
    "12": "https://blog.4geeks.io/building-a-production-ready-rag-system-from-scratch-an-architectural-deep-dive/"
}


def read_prompt(prompt_file: str) -> str:
    """Read the prompt template from file."""
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file '{prompt_file}' not found")


def fetch_url_content(url: str) -> str:
    """
    Fetch content from URL using requests library.

    Args:
        url: The URL to fetch

    Returns:
        The content from the URL as text
    """
    try:
        print(f"  Fetching content from URL...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  Warning: Could not fetch URL content: {e}")
        return f"[Error fetching content: {e}]"


def call_claude_api(client: Anthropic, prompt: str, article_content: str) -> str:
    """
    Call Claude API with the prompt and article content.

    Args:
        client: Anthropic client instance
        prompt: The base prompt text
        article_content: The fetched content from the article URL

    Returns:
        The API response text
    """
    # Combine prompt with article content
    full_prompt = f"{prompt}\n\n--- Article Content ---\n\n{article_content}"

    # Call Claude API
    message = client.messages.create(
        model=MODEL,
        max_tokens=8096,
        messages=[
            {"role": "user", "content": full_prompt}
        ]
    )

    return message.content[0].text


def save_result(content: str, key: str, output_dir: str) -> str:
    """
    Save the API result to a file.

    Args:
        content: The content to save
        key: The article key/identifier
        output_dir: Directory to save the file in

    Returns:
        Path to the saved file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Format filename with key
    filename = f"{key}-chatgpt-prompt-vs-claude-api.md"
    filepath = os.path.join(output_dir, filename)

    # Save content to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath


def process_articles(article_urls: dict, prompt_file: str, prefix: str, output_dir: str):
    """
    Process all articles with Claude API.

    Args:
        article_urls: Dictionary mapping article keys to URLs
        prompt_file: Path to the prompt template file
        output_dir: Directory to save results
        prefix: Prefix to add to file name
    """
    # Initialize Anthropic client
    # Ensure ANTHROPIC_API_KEY is set in environment variables
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Read the base prompt
    print(f"Reading prompt from '{prompt_file}'...")
    base_prompt = read_prompt(prompt_file)

    # Process each article
    total = len(article_urls)
    for index, (key, article_url) in enumerate(article_urls.items(), start=1):
        print(f"\n[{index}/{total}] Processing '{key}': {article_url}")

        try:
            # Fetch article content
            article_content = fetch_url_content(article_url)

            # Call Claude API
            print(f"  Calling Claude API...")
            result = call_claude_api(client, base_prompt, article_content)

            # Save result
            output_path = save_result(result, f'{key}-{prefix}', output_dir)
            print(f"  ✓ Saved to: {output_path}")

        except Exception as e:
            print(f"  ✗ Error processing article: {e}")
            continue

    print(f"\n✓ Completed processing {total} articles")


def main():
    """Main entry point."""
    # Validate API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Please generate one at: https://console.anthropic.com/settings/keys "
            "and set it with: export ANTHROPIC_API_KEY='your_api_key_here'"
        )

    # Process articles with ChatGPT generated prompt
    process_articles(ARTICLE_URLS, "02-result-chatgpt-research-paper-analysis-prompt.md", "chatgpt", OUTPUT_DIR)

    # Process articles with Claude Code generated prompt
    process_articles(ARTICLE_URLS, "03-result-claude-code-prompt.md", "claude-code", OUTPUT_DIR)


if __name__ == "__main__":
    main()
