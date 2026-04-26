import os

markdown_content = """# LexGuard: Production-Grade Local RAG System
## Project Goal
Build a GDPR-compliant, privacy-first AI Document Assistant for the German 'Mittelstand' using local LLMs and agentic workflows.

---

## 🛠 Tech Stack
- **AI Engine:** Ollama (Mistral-Nemo / Llama 3.1)
- **Orchestration:** LangGraph (State Machine for AI agents)
- **Database:** Qdrant (Hybrid Search: Vector + BM25)
- **API:** FastAPI (Asynchronous Python)
- **Frontend:** Streamlit
- **Infrastructure:** Docker & Docker-Compose
- **Hardware:** Optimized for Apple Silicon (Mac M3 Unified Memory)

---

## 📅 Phase 1: Infrastructure & Environment (Days 1-2)
- [ ] **Setup Poetry:** Initialize environment and manage dependencies.
- [ ] **Dockerize Qdrant:** Set up persistent volume mapping to `./qdrant_data`.
- [ ] **Ollama Setup:** Download and test `mistral-nemo` locally.
- [ ] **Project Structure:** Create the modular directory (`/src`, `/data`, `/tests`).

## 📅 Phase 2: The Data Engine (Days 3-5)
- [ ] **Ingestion Pipeline:** Build logic to load PDFs and split them without breaking German compound words.
- [ ] **Hybrid Search:** Configure Qdrant for both Dense (semantic) and Sparse (keyword) embeddings.
- [ ] **FastAPI Endpoints:**
    - `POST /ingest`: Upload and index documents.
    - `GET /search`: Test retrieval accuracy.

## 📅 Phase 3: The Agentic Brain (Days 6-8)
- [ ] **LangGraph Implementation:** - **Node 1 (Retrieve):** Fetch context from Qdrant.
    - **Node 2 (Grade):** Use LLM to verify if the context actually answers the question.
    - **Node 3 (Generate):** Produce the final answer or a "safety refusal."
- [ ] **Prompt Engineering:** Optimize system prompts for German professional tone (Sie-form).

## 📅 Phase 4: Frontend & Observability (Days 9-11)
- [ ] **Streamlit UI:** Create a "Chat with your Docs" interface.
- [ ] **Observability:** Integrate **Langfuse** (local) to trace every step of the graph.
- [ ] **Logging:** Replace all `print()` statements with Python's `logging` module.

## 📅 Phase 5: Quality Assurance & Resume (Days 12-14)
- [ ] **Evaluation (RAGAS):** Run a script to score 10 sample queries for "Faithfulness."
- [ ] **Unit Tests:** Write tests for the API using `pytest`.
- [ ] **Documentation:** Write a professional README with an architecture diagram.
- [ ] **GitHub:** Push code with a clean commit history.

---

## 🇩🇪 Resume Bullet Points (Copy-Paste)
**AI Engineer Project | LexGuard – Production-Grade Local RAG System**
* Developed a **GDPR-compliant** RAG system on **macOS (M3)** using **Python** and **Qdrant**, ensuring 100% data sovereignty.
* Implemented **Hybrid Search** (Dense + Sparse) to handle complex German compound nouns, improving retrieval precision.
* Architected an **Agentic Workflow** using **LangGraph** with a self-correction loop to eliminate hallucinations.
* Containerized the stack using **Docker** and implemented full-trace observability using **Langfuse**.

---

## 🚀 Commands to Start
```bash
# Start Database
docker run -d -p 6333:6333 -v "$(pwd)/qdrant_data:/qdrant/storage:z" qdrant/qdrant

# Install Deps
poetry add fastapi uvicorn langgraph qdrant-client langchain-community streamlit ragas

# Run API
uvicorn src.main:app --reload