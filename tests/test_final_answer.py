from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine import ask_lexguard

if __name__ == "__main__":
    query = "What is the invoice number?"

    print("LexGuard is processing the query...")
    answer = ask_lexguard(query)

    print("\nFinal answer:")
    print(answer)