import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine import lexguard_agent

def run_positive_test():
    """Verify that the agent answers a document-related query."""
    print("\n--- POSITIVE TEST: VALID INQUIRY ---")
    inputs = {"question": "What is the invoice number?"}

    result = lexguard_agent.invoke(inputs)

    if "generation" in result:
        print(f"LexGuard response: {result['generation']}")
    else:
        print("Test failed: the agent refused to answer a valid question.")

def run_negative_test():
    """Verify that the agent refuses irrelevant queries."""
    print("\n--- NEGATIVE TEST: IRRELEVANT INQUIRY ---")
    inputs = {"question": "What is the capital of France?"}

    result = lexguard_agent.invoke(inputs)

    if "generation" not in result:
        print("Success: the agent correctly identified the context as irrelevant.")
    else:
        print(f"Test failed: the agent answered an irrelevant query: {result['generation']}")

if __name__ == "__main__":
    run_positive_test()
    run_negative_test()