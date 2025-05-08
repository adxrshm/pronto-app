# agent.py
import os
import re
import json
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from vector_store import query_vector_store  # Your custom Pinecone search function

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimplePineconeResearchAgent:
    """A simpler agent that directly uses OpenAI without the LangChain agent framework."""

    def __init__(self, model_name="gpt-4-turbo", debug=False, max_results_to_show=5):
        """Initialize the agent with direct LLM access."""
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=openai_api_key
        )

        self.debug = debug
        self.max_results_to_show = max_results_to_show

        self.prompt_template = PromptTemplate(
            input_variables=["query", "search_results"],
            template="""You are a helpful research assistant with access to a specialized knowledge base.

I've searched the knowledge base for information related to: {query}

Here are the search results:
{search_results}

Based on these search results, please provide a comprehensive answer to the query. 
If the results contain specific details, include them in your answer.
If the search results don't seem relevant or don't provide enough information, 
acknowledge this and provide a general answer based on your knowledge.

Always prioritize information from the search results over your general knowledge when available."""
        )

    def format_result(self, result, index):
        """Format a single result for display and LLM input."""
        if hasattr(result, 'page_content'):
            return f"Result {index}:\n{result.page_content}"
        elif hasattr(result, 'metadata') and 'text' in result.metadata:
            return f"Result {index}:\n{result.metadata['text']}"
        else:
            try:
                return f"Result {index}:\n{json.dumps(result, indent=2)}"
            except:
                return f"Result {index}:\n{str(result)}"

    def is_greeting(self, text):
        """Check if the user input is a greeting."""
        text = text.strip().lower()
        return re.match(r"^(hi+|hello+|hey+|heya+|yo+|hai+)[!.\s]*$", text)

    def query(self, user_input):
        """Process a user query and return the response."""
        try:
            logger.info(f"Processing query: {user_input}")

            # Handle greetings directly
            if self.is_greeting(user_input):
                return "Hello! How can I assist you with your research today?"

            # Query the vector store
            results = query_vector_store(user_input)

            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append(self.format_result(result, i + 1))

            if self.debug:
                print("\n--- DEBUG: Direct Vector Store Query ---")
                print(f"Found {len(results)} results directly from vector store")

                display_count = min(len(results), self.max_results_to_show)
                for i in range(display_count):
                    print(f"\n{formatted_results[i]}")
                if len(results) > self.max_results_to_show:
                    print(f"\n... {len(results) - self.max_results_to_show} more results not shown ...")
                print("--- End of Direct Query Results ---\n")

            all_results_text = "\n\n".join(formatted_results)

            prompt = self.prompt_template.format(
                query=user_input,
                search_results=all_results_text
            )

            response = self.llm.invoke(prompt)
            return response.content

        except Exception as e:
            logger.exception(f"Error processing query: {e}")
            return f"Error processing your query: {str(e)}"


# Optional: Command-line interface
if __name__ == "__main__":
    print("\n===== Pinecone Research Assistant =====\n")
    print("Initializing agent...")

    try:
        agent = SimplePineconeResearchAgent(debug=True)
        print("Agent initialized successfully!")
        print("\nType your questions below. Type 'exit' to quit.\n")

        while True:
            user_input = input("\nQuestion: ")
            if user_input.lower() in ["exit", "quit"]:
                print("\nGoodbye!")
                break

            print("\nSearching knowledge base...")
            response = agent.query(user_input)
            print(f"\nAnswer: {response}")

    except Exception as e:
        logger.exception("Error initializing agent")
        print(f"Error: {str(e)}")
        print("Make sure your environment variables (OPENAI_API_KEY, PINECONE_API_KEY) are set correctly.")
