import os
from openai import OpenAI
from pathlib import Path

from gpt_model import GPTModel
from sql_query_assistant import SQLQueryAssistant
from data_preparator import DataPreparator

DB_METADATA_FILE = Path(__file__).parent / "data" / "ready" / "northwind_schema.json"
DB_FILE_PATH = Path(__file__).parent / "data" / "ready" / "northwind.db"
GPT_MODEL_SQL_ASSISTANT = GPTModel("gpt-5-mini")
GPT_MODEL_PREPARE_DATA = GPTModel("gpt-5")


def main():
    """Main CLI loop for the query assistant."""

    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please generate one at: https://platform.openai.com/docs/quickstart")
        print("and set it with: export OPENAI_API_KEY='your_api_key_here'")
        return

    client = OpenAI(api_key=api_key)

    # Initialize data
    if not os.path.exists(DB_METADATA_FILE):
        data_prep = DataPreparator(client, GPT_MODEL_PREPARE_DATA)
        data_prep.prepare_sql_data()

    # Initialize SQL Query Assistant
    try:
        assistant = SQLQueryAssistant(client, DB_METADATA_FILE, GPT_MODEL_SQL_ASSISTANT, DB_FILE_PATH)
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
            analysis = assistant.analyze_question(question)

            if analysis:
                assistant.display_analysis(analysis)
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
