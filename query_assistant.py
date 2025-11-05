import os
import time
from openai import OpenAI
from pathlib import Path

from gpt_model import ApiStatistics, GPTModel
from sql_query_assistant import SQLQueryAssistant
from data_preparator import DataPreparator

DB_METADATA_FILE = Path(__file__).parent / "data" / "ready" / "northwind_schema.json"
DB_FILE_PATH = Path(__file__).parent / "data" / "ready" / "northwind.db"
GPT_MODEL_SQL_ASSISTANT = GPTModel("gpt-5-mini")
GPT_MODEL_PREPARE_DATA = GPTModel("gpt-5")
GPT_MODEL_ANSWER_GENERATOR = GPTModel("gpt-5-mini")


def generate_answer(client: OpenAI, gpt_model: GPTModel, question: str, sql_results: list) -> tuple[dict, ApiStatistics]:
    """
    Generate a natural language answer based on SQL query results.

    Args:
        client: OpenAI client instance
        gpt_model: GPTModel instance for the API call
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

        response = client.chat.completions.create(
            model=gpt_model.model_name,
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
        statistics = gpt_model.prepare_statistics(elapsed_time, response.usage)

        answer = response.choices[0].message.content

        return answer, statistics

    except Exception as e:
        return f"Error generating answer: {str(e)}", None


def main():
    """Main CLI loop for the query assistant."""

    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please generate one at: https://platform.openai.com/docs/quickstart")
        print("and set it with: export OPENAI_API_KEY='your_api_key_here'")
        return

    # Parse SQL_DEBUG environment variable to boolean
    sql_debug = os.getenv('SQL_DEBUG', 'true').lower() in ('true', '1', 'yes')

    client = OpenAI(api_key=api_key)

    # Initialize data
    if not os.path.exists(DB_METADATA_FILE):
        data_prep = DataPreparator(client, GPT_MODEL_PREPARE_DATA)
        data_prep.prepare_sql_data()

    # Initialize SQL Query Assistant
    try:
        sql_assistant = SQLQueryAssistant(client, DB_METADATA_FILE, GPT_MODEL_SQL_ASSISTANT, DB_FILE_PATH)
    except Exception as e:
        print(f"Error initializing SQL assistant: {e}")
        return

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
            sql_analysis, sql_analysis_stats = sql_assistant.analyze_question(question)

            if sql_analysis:
                sql_debug_info, sql_gpt_input = sql_assistant.process_analysis(sql_analysis)

                # Generate natural language answer
                print("\n⏳ Generating answer...")
                answer, answer_stats = generate_answer(
                    client,
                    GPT_MODEL_ANSWER_GENERATOR,
                    question,
                    sql_gpt_input
                )

                # Display the answer
                print("\n" + "="*80)
                print("ANSWER")
                print("="*80)
                print(f"\n{answer}\n")
                print("="*80)
                if answer_stats:
                    answer_stats.sum(sql_analysis_stats).print()

                if sql_debug:
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


if __name__ == "__main__":
    main()
