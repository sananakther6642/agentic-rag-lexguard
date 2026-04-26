import sys
from pathlib import Path
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama

# Ensure project root is in path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import search_knowledge

# Define the shared data structure between nodes
class GraphState(TypedDict):
    question: str
    documents: List[str]
    generation: str
    relevance: str 

# Use a temperature of 0 for deterministic, repeatable grading
model = ChatOllama(model="mistral-nemo", temperature=0)

def retrieve_node(state: GraphState):
    """Fetches documents from the vector database based on the query."""
    docs = search_knowledge(state["question"])
    # Extract only text content for the model to process
    doc_texts = [d.page_content for d in docs]
    return {"documents": doc_texts}

def grade_node(state: GraphState):
    """Filters retrieved documents based on their relevance to the question."""
    context = "\n".join(state["documents"])
    # Grader prompt designed to force a binary 'yes' or 'no' response
    prompt = (
        f"Analyze if this context answers the question.\n"
        f"Context: {context}\n"
        f"Question: {state['question']}\n"
        f"Reply only with 'yes' or 'no'."
    )
    res = model.invoke(prompt)
    decision = res.content.strip().lower()
    return {"relevance": "yes" if "yes" in decision else "no"}

def generate_node(state: GraphState):
    """Produces the final response using only the validated context."""
    context = "\n".join(state["documents"])
    prompt = f"Answer the question using only the provided context:\nContext: {context}\nQuestion: {state['question']}"
    res = model.invoke(prompt)
    return {"generation": res.content}

# Initialize the state machine
workflow = StateGraph(GraphState)

# Define the computational steps as nodes
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("grade", grade_node)
workflow.add_node("generate", generate_node)

# Define the execution path
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade")

# Logic gate: route to generation only if the grader approves relevance
workflow.add_conditional_edges(
    "grade",
    lambda x: x["relevance"],
    {
        "yes": "generate",
        "no": END
    }
)
workflow.add_edge("generate", END)

# Compile the graph into an executable agent
lexguard_agent = workflow.compile()