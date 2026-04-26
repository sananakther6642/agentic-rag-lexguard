from importlib import import_module

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="LexGuard Production API")

class QueryRequest(BaseModel):
    prompt: str

@app.post("/ask")
async def ask_lexguard(request: QueryRequest):
    """
    The Production Entry Point: 
    Retrieves, Grades, and Generates using the LangGraph loop.
    """
    try:
        try:
            graph_engine = import_module("src.engine").app
        except ImportError as import_error:
            raise HTTPException(
                status_code=500,
                detail="Graph engine not configured. Add src/engine.py with an `app` graph object.",
            ) from import_error

        # Initial state for our Graph
        inputs = {"question": request.prompt, "documents": [], "relevance": "no"}
        
        # Run the Graph (Self-Correction Logic)
        result = graph_engine.invoke(inputs)
        
        # If the grader found no relevant docs
        if result.get("relevance") == "no":
            return {
                "answer": "I'm sorry, but I couldn't find any relevant information in the internal documents to answer this safely.",
                "sources": []
            }

        return {
            "answer": result["generation"],
            "sources": result["documents"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
