import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import process_document
from src.engine import lexguard_agent

if __name__ == "__main__":
    process_document("data/invoice.pdf")
    process_document("data/payroll.pdf")

    query = "Who is the sender?"

    print("\n--- TARGETING: invoice.pdf ---")
    res1 = lexguard_agent.invoke({
        "question": query,
        "target_file": "invoice.pdf"
    })
    print(f"Result: {res1.get('generation')}")

    print("\n--- TARGETING: payroll.pdf ---")
    res2 = lexguard_agent.invoke({
        "question": query,
        "target_file": "payroll.pdf"
    })
    print(f"Result: {res2.get('generation')}")