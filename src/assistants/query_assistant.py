import os
import time
from openai import OpenAI

from src.models.gpt_model import ApiStatistics
from src.assistants.sql_query_assistant import SQLQueryAssistant
from src.assistants.text_query_assistant import TextQueryAssistant
from src.data_processing.sql_data_preparator import SqlDataPreparator
from src.data_processing.text_data_preparator import TextDataPreparator
from src.config.config import Config


class QueryAssistant:
    """Main query assistant class for handling user questions."""

    def __init__(self, config: Config):
        """
        Initialize the QueryAssistant.

        Args:
            config: Application configuration including models, paths, and settings
        """
        # Store config
        self.config = config

        # Get API key
        if not config.open_ai_api_key:
            raise ValueError(
                "OpenAI API key not provided. "
                "Please generate one at: https://platform.openai.com/docs/quickstart "
                "and set it with: export OPENAI_API_KEY='your_api_key_here'"
            )

        # Initialize OpenAI client
        self.client = OpenAI(api_key=config.open_ai_api_key)

        # Prepare data if needed
        self._prepare_data()

        # Initialize SQL Query Assistant
        try:
            self.sql_assistant = SQLQueryAssistant(self.client, self.config)
        except Exception as e:
            raise RuntimeError(f"Error initializing SQL assistant: {e}")

        # Initialize Text Query Assistant
        try:
            self.text_assistant = TextQueryAssistant(self.client, self.config, use_sentence_chunks=False)
        except Exception as e:
            raise RuntimeError(f"Error initializing text assistant: {e}")

    def _prepare_data(self):
        """Prepare database and article data if not already prepared."""
        if not os.path.exists(self.config.file_sql_metadata):
            data_prep = SqlDataPreparator(self.client, self.config)
            data_prep.prepare_sql_data()

        if not os.path.exists(self.config.file_articles_sentences) or not os.path.exists(self.config.file_articles_length):
            text_preparator = TextDataPreparator(self.client, self.config)
            text_preparator.prepare_articles()

    def process_sql_query(self, question: str) -> tuple[str, str, ApiStatistics]:
        """
        Process question using SQL assistant.

        Args:
            question: User's question

        Returns:
            ApiStatistics for the SQL operations
        """
        stats = ApiStatistics.empty()
        print("\n⏳ Analyzing your question with SQL...")
        sql_analysis, sql_analysis_stats = self.sql_assistant.analyze_question(question)
        stats = stats.sum(sql_analysis_stats)

        if sql_analysis:
            sql_debug = []
            sql_debug_info, sql_gpt_input = self.sql_assistant.process_analysis(sql_analysis)

            sql_debug.append("\n" + "="*80)
            sql_debug.append("DETAILED SQL ANALYSIS")
            sql_debug.append("="*80)
            sql_debug.extend(sql_debug_info)
            sql_debug.append("="*80)

            return "\n".join(sql_gpt_input), "\n".join(sql_debug), stats
        else:
            print("\n❌ Failed to analyze the question with SQL.")
            return "No SQL information available", ApiStatistics.empty()

    def process_text_query(self, question: str, top_k: int = 5) -> tuple[str, str, ApiStatistics]:
        """
        Process question using text assistant.

        Args:
            question: User's question
            top_k: Number of top results to return

        Returns:
            ApiStatistics for the text search operations
        """
        stats = ApiStatistics.empty()
        print("\n⏳ Searching articles...")
        semantic_results, keyword_results, query_debug, text_search_stats = self.text_assistant.search(question, top_k)
        stats = stats.sum(text_search_stats)

        semantic_article_ids = []
        text_prompt = []
        text_debug = []
        text_debug.append("\n" + "="*80)
        text_debug.append("QUERY INFO")
        text_debug.append("="*80)
        text_debug.extend(query_debug)

        text_debug.append("\n" + "="*80)
        text_debug.append("SEMANTIC SEARCH RESULTS (Top 5)")
        text_debug.append("="*80)
        for idx, result in enumerate(semantic_results, 1):
            semantic_article_ids.append(result['id'])
            text_prompt.append(f"Title: {result['title']}, Text: {result['text']}")
            text_debug.append(f"\n{idx}. Article: {result['id']}")
            text_debug.append(f"   Title: {result['title']}")
            text_debug.append(f"   Similarity: {result['similarity']:.4f}")
            text_debug.append(f"   Text: {result['text'][:100]}...")

        text_debug.append("\n" + "="*80)
        text_debug.append("KEYWORD SEARCH RESULTS (Top 5)")
        text_debug.append("="*80)

        use_keyword_article = True
        for idx, result in enumerate(keyword_results, 1):
            # Append only one article from the keyword search that is not already in semantic results
            if use_keyword_article and result['id'] not in semantic_article_ids:
                use_keyword_article = False
                text_prompt.append(f"Title: {result['title']}, Text: {result['text']}")

            text_debug.append(f"\n{idx}. Article: {result['id']}")
            text_debug.append(f"   Title: {result['title']}")
            text_debug.append(f"   Matches: {result['match_count']} ({', '.join(result['matched_keywords'])})")
            text_debug.append(f"   Text: {result['text'][:100]}...")

        return "\n".join(text_prompt), "\n".join(text_debug), stats

    def generate_answer(self, question: str, sql_prompt: str, text_prompt: str) -> tuple[str, ApiStatistics]:
        """
        Generate a natural language answer based on SQL query results.

        Args:
            question: User's original question
            sql_results: List of strings containing SQL query results

        Returns:
            Tuple of (answer: str, statistics: ApiStatistics)
        """

        prompt = f"""You are a helpful assistant that answers questions based on database query results.

User Question: {question}

SQL Query Results:
{sql_prompt}

Text Search Results:
{text_prompt}

Based on the SQL query results above and the text search results, provide a clear, concise, and accurate answer to the user's question.
Format your response in a natural, conversational way. If the results show data in tables, summarize the key findings.
If there are no results or the query failed, explain that appropriately.

Do not suggest to do any follow up actions.
Do not mention the SQL queries or database structure in your answer.
Do not provide any external knowledge outside of the input data.
Do not reference to other data sources."""

        try:
            # Start timing
            start_time = time.time()

            response = self.client.chat.completions.create(
                model=self.config.model_answer_generator.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful database assistant that provides clear answers based on SQL query results."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )

            # End timing
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Calculate statistics
            statistics = self.config.model_answer_generator.prepare_statistics(elapsed_time, response.usage)

            answer = response.choices[0].message.content

            return answer, statistics

        except Exception as e:
            return f"Error generating answer: {str(e)}", ApiStatistics.empty()

    def run(self):
        """Main CLI loop for the query assistant."""
        # Display welcome message
        print("\n" + "="*80)
        print("QUERY ASSISTANT")
        print("="*80)
        print("\nWelcome! Ask questions about our company data.")
        print("\nType 'exit' or 'quit' to end the session.\n")

        # Main loop
        while True:
            try:
                # Get user input
                question = input("💬 Your question: ").strip()

                if not question:
                    continue

                if question.lower() in ['exit', 'quit', 'q']:
                    print("\nGoodbye! 👋")
                    break

                # Track statistics
                stats = ApiStatistics.empty()

                # Process SQL query
                sql_prompt, sql_debug, sql_stats = self.process_sql_query(question)
                stats = stats.sum(sql_stats)

                # Process text query
                text_prompt, text_debug, text_stats = self.process_text_query(question, top_k=5)
                stats = stats.sum(text_stats)

                # Generate natural language answer
                print("\n⏳ Generating answer...")
                answer, answer_stats = self.generate_answer(question, sql_prompt, text_prompt)
                stats = stats.sum(answer_stats)

                # Display the answer
                print("\n" + "="*80)
                print("ANSWER")
                print("="*80)
                print(f"\n{answer}\n")
                print("="*80)
                stats.print()
                print("="*80)
                print("\n")

                # Display SQL debug info if enabled
                if self.config.sql_search_debug:
                    print("\n")
                    print(sql_debug)
                    print("\n")

                # Display text debug info if enabled
                if self.config.text_search_debug:
                    print("\n")
                    print(text_debug)
                    print("\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print("Please try again.\n")
