import sys
from pathlib import Path
from langchain_ollama import ChatOllama

# --- Professor's Pathing Rule ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import search_knowledge

# 1. Initialize the Reasoning Engine (Mistral-Nemo)
# Temperature 0 makes the AI "strict" and less likely to imagine things.
llm = ChatOllama(model="mistral-nemo", temperature=0)

def ask_lexguard(question: str):
    # A. Retrieve the relevant snippets (What you just did manually)
    context_docs = search_knowledge(question)
    context_text = "\n\n".join([doc.page_content for doc in context_docs])
    
    # B. Build the "Sandwich" Prompt
    prompt = f"""
    You are LexGuard, a professional assistant. 
    Use the following retrieved context to answer the user's question.
    If the answer is not in the context, say you do not know. 
    Do not use outside knowledge.

    CONTEXT:
    {context_text}

    USER QUESTION: 
    {question}

    ANSWER:
    """
    
    # C. Get the response from your M3 GPU
    response = llm.invoke(prompt)
    return response.content