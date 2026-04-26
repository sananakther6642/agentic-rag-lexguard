from pathlib import Path
import sys

# Since this is in /tests, we go up one level to find /src
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import search_knowledge

if __name__ == "__main__":
    # Ask a question that is actually in your invoice!
    # Example: "What is the total amount due?" or "Who is the sender?"
    user_query = "What is the total amount on this invoice?"
    
    print(f"--- Searching for '{user_query}' ---")
    
    hits = search_knowledge(user_query)
    
    if not hits:
        print("❌ No results found. Did you run the ingestion script first?")
    else:
        for i, hit in enumerate(hits):
            print(f"\n[Match {i+1}] (Score: {hit.metadata.get('_score', 'N/A')})")
            print(f"Content: {hit.page_content[:200]}...")