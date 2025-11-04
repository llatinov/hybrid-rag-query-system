# Generate python scripts to automatically get the articles summary based on the given prompts

Generate python code that iterates over list of article URLs which are defined as a map with key:value, reads the "prompt.md" file, performs a curl on the URL and adds the curl output as part of the prompt, calls OpenAI API using its SDK and saved the result onto a file with name <key_from_the_map>-chatgpt.
