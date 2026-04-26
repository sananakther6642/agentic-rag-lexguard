import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine import lexguard_agent

if __name__ == "__main__":
    print("\n--- TRACEABILITY TEST: FULL STATE INSPECTION ---")
    query = "Who is the sender of this invoice?"

    final_state = lexguard_agent.invoke({"question": query})

    print("\n[INTERNAL STATE TRACE]")
    for key, value in final_state.items():
        display_val = str(value)[:100] + "..." if isinstance(value, str) and len(value) > 100 else value
        print(f"Key: {key} | Value: {display_val}")