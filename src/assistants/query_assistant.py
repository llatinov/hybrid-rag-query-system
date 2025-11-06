import os
import time
from openai import OpenAI

from src.models.gpt_model import ApiStatistics
from src.assistants.sql_query_assistant import SQLQueryAssistant
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

    def _prepare_data(self):
        """Prepare database and article data if not already prepared."""
        if not os.path.exists(self.config.file_sql_metadata):
            data_prep = SqlDataPreparator(self.client, self.config)
            data_prep.prepare_sql_data()

        if not os.path.exists(self.config.file_articles_sentences) or not os.path.exists(self.config.file_articles_length):
            text_preparator = TextDataPreparator(self.client, self.config)
            text_preparator.prepare_articles()

    def generate_answer(self, question: str, sql_results: list) -> tuple[str, ApiStatistics]:
        """
        Generate a natural language answer based on SQL query results.

        Args:
            question: User's original question
            sql_results: List of strings containing SQL query results

        Returns:
            Tuple of (answer: str, statistics: ApiStatistics)
        """
        # Join SQL results into a single text block
        sql_results_text = "\n".join(sql_results)

        prompt = f"""You are a helpful assistant that answers questions based on database query results.

User Question: {question}

SQL Query Results:
{sql_results_text}

Based on the SQL query results above, provide a clear, concise, and accurate answer to the user's question.
Format your response in a natural, conversational way. If the results show data in tables, summarize the key findings.
If there are no results or the query failed, explain that appropriately."""

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
            return f"Error generating answer: {str(e)}", None

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

                # Analyze the question
                print("\n⏳ Analyzing your question...")
                sql_analysis, sql_analysis_stats = self.sql_assistant.analyze_question(question)

                if sql_analysis:
                    sql_debug_info, sql_gpt_input = self.sql_assistant.process_analysis(sql_analysis)

                    # Generate natural language answer
                    print("\n⏳ Generating answer...")
                    answer, answer_stats = self.generate_answer(question, sql_gpt_input)

                    # Display the answer
                    print("\n" + "="*80)
                    print("ANSWER")
                    print("="*80)
                    print(f"\n{answer}\n")
                    print("="*80)
                    if answer_stats:
                        answer_stats.sum(sql_analysis_stats).print()

                    if self.config.sql_debug:
                        print("\n" + "="*80)
                        print("DETAILED SQL ANALYSIS")
                        print("="*80)
                        print("\n".join(sql_debug_info))
                        print("="*80)
                        if sql_analysis_stats:
                            sql_analysis_stats.print()

                else:
                    print("\n❌ Failed to analyze the question. Please try again.")

                print("\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print("Please try again.\n")
