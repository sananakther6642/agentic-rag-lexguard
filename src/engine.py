import sys
from pathlib import Path
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import search_knowledge

class GraphState(TypedDict):
    question: str
    documents: List[str]
    generation: str
    relevance: str
    target_file: str
    loop_count: int

# Shared model used across retrieval, grading, and generation.
model = ChatOllama(model="qwen2.5:3b", temperature=0)

def retrieve_node(state: GraphState):
    """
    Retrieve supporting passages for the current query.
    """
    print("--- AGENT: EXECUTING RETRIEVAL ---")

    question = state.get("question")
    target_file = state.get("target_file")

    docs = search_knowledge(
        query=question,
        filter_file=target_file,
        k=10
    )

    doc_texts = [d.page_content for d in docs]
    return {"documents": doc_texts}

def grade_node(state: GraphState):
    """
    Determine whether the retrieved context is relevant enough to answer.
    """
    print("--- AGENT: DYNAMIC SEMANTIC GRADING ---")

    if not state["documents"]:
        return {"relevance": "no"}

    context = "\n".join(state["documents"])

    prompt = (
        f"SYSTEM: You are a strict Information Validator.\n"
        f"TASK: Determine whether the context contains information that can help answer the user question.\n\n"
        f"USER QUESTION: {state['question']}\n"
        f"CONTEXT: {context}\n\n"
        f"EVALUATION CRITERIA:\n"
        f"- Return 'yes' if the context directly or indirectly helps answer the question.\n"
        f"- Return 'no' if the context is unrelated or does not contain the needed information.\n\n"
        f"REPLY ONLY WITH 'yes' OR 'no':"
    )

    res = model.invoke(prompt)
    decision = res.content.strip().lower()

    final_decision = "yes" if "yes" in decision else "no"

    print(f"DEBUG: Universal Grader Decision -> {final_decision}")
    return {"relevance": final_decision}

def generate_node(state: GraphState):
    """
    Generate the final answer from the validated context.
    """
    print("--- AGENT: ZERO-SHOT INVARIANT INFERENCE ---")

    context = "\n\n".join(state["documents"])

    prompt = (
        f"CONTEXT MANIFOLD:\n{context}\n\n"
        f"QUERY: {state['question']}\n\n"
        f"Answer the question using only the context above."
    )

    res = model.invoke(prompt)
    return {"generation": res.content}

def unified_reasoning_node(state: GraphState):
    """
    Extract a grounded answer from the retrieved context.
    """
    print("--- AGENT: EXECUTING ZERO-SHOT INFERENCE ---")

    context = "\n\n".join(state["documents"])

    prompt = (
        f"CONTEXT MANIFOLD:\n{context}\n\n"
        f"QUERY: {state['question']}\n\n"
        f"Return a grounded answer from the context."
    )

    res = model.invoke(prompt)
    content = res.content

    relevance = "yes" if "RELEVANCE: YES" in content.upper() else "no"
    clean_generation = content.replace("RELEVANCE: YES", "").replace("RELEVANCE: NO", "").strip()

    return {
        "generation": clean_generation,
        "relevance": relevance
    }

def transform_query_node(state: GraphState):
    """
    Rewrite the query when the first retrieval pass is not sufficient.
    """
    print("--- AGENT: REWRITING QUERY FOR BETTER MANIFOLD PROBING ---")
    print(f"--- AGENT: ATTEMPT {state.get('loop_count', 0) + 1} ---")
    query = state["question"]

    prompt = (
        f"You are a retrieval optimizer. The initial search for '{query}' did not return enough context.\n"
        f"Rewrite the query to be broader and more specific to document content.\n"
        f"OUTPUT ONLY THE NEW QUERY:"
    )

    res = model.invoke(prompt)
    return {
        "question": res.content.strip(),
        "loop_count": state.get("loop_count", 0) + 1
    }

def decide_to_generate(state: GraphState):
    iteration = state.get("loop_count", 0)

    if state["relevance"] == "yes" or iteration >= 2:
        return "generate"

    return "rewrite"

def route_intent(state: GraphState):
    query = state["question"].lower()
    summary_triggers = ["about", "summary", "overview", "what is this", "general"]

    if any(word in query for word in summary_triggers):
        print("\n[TRACE] Router Decision: SUMMARY FAST-TRACK")
        return "summary"

    print("\n[TRACE] Router Decision: SPECIFIC RETRIEVAL")
    return "retrieve"

def summary_node(state: GraphState):
    print("[TRACE] Executing Summary Node...")

    docs = search_knowledge(state["question"], filter_file=state["target_file"], k=4)
    context = "\n\n".join([d.page_content for d in docs])

    prompt = (
        f"CONTEXT MANIFOLD:\n{context}\n\n"
        f"TASK: Provide a concise high-level summary of this document.\n"
        f"OUTPUT:"
    )

    res = model.invoke(prompt)
    return {
        "generation": res.content,
        "relevance": "yes",
        "documents": [d.page_content for d in docs]
    }

workflow = StateGraph(GraphState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("summary", summary_node)
workflow.add_node("reasoning", grade_node)
workflow.add_node("generate", generate_node)
workflow.add_node("rewrite", transform_query_node)

workflow.set_conditional_entry_point(
    route_intent,
    {
        "summary": "summary",
        "retrieve": "retrieve"
    }
)
workflow.add_edge("summary", END)
workflow.add_edge("retrieve", "reasoning")

workflow.add_conditional_edges(
    "reasoning",
    decide_to_generate,
    {
        "generate": END,
        "rewrite": "rewrite"
    }
)
workflow.add_edge("rewrite", "retrieve")

lexguard_agent = workflow.compile()


def ask_lexguard(question: str, target_file: str = None):
    """Run the agent for a single question and return the generated answer."""
    inputs = {
        "question": question,
        "target_file": target_file,
        "documents": [],
        "relevance": "",
        "loop_count": 0,
    }
    result = lexguard_agent.invoke(inputs)
    return result.get("generation", "")