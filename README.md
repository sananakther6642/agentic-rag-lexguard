# LexGuard AI

LexGuard AI is a local document assistant for PDF ingestion, retrieval, and question answering. It uses Qdrant for vector storage, Ollama for local model inference, and LangGraph for the agent workflow.

## Features

- PDF ingestion with page-level chunking and metadata.
- Qdrant-backed similarity search with optional file filtering.
- LangGraph agent flow with retrieval, grading, rewriting, and generation.
- Streamlit interface for uploading documents and asking questions.
- Local model configuration with `qwen2.5:3b`.

## Tech Stack

- Python 3.11
- Poetry
- LangChain and LangGraph
- Qdrant
- Ollama
- Streamlit

## Project Layout

```text
LexGuard/
├── docker-compose.yml
├── pyproject.toml
├── README.md
├── src/
│   ├── database.py
│   ├── engine.py
│   └── ui.py
└── tests/
    ├── test_agent_logic.py
    ├── test_agent_traces.py
    ├── test_final_answer.py
    └── test_multiple_files.py
```

## Setup

Install dependencies with Poetry:

```bash
poetry install
```

Activate the environment if needed:

```bash
poetry shell
```

## Local Services

Start Qdrant with Docker:

```bash
docker compose up -d qdrant
```

Make sure Ollama is running locally and that the `qwen2.5:3b` model is available.

## Usage

Run the Streamlit UI:

```bash
poetry run streamlit run src/ui.py
```

The UI lets you upload a PDF, index it, and ask questions about the document.

## Core Workflow

1. `src/database.py` loads PDFs, splits them into chunks, and stores them in Qdrant.
2. `src/engine.py` runs the LangGraph agent and handles retrieval, grading, query rewriting, and answer generation.
3. `src/ui.py` provides the Streamlit interface for upload and chat.

## Test Scripts

The repository includes script-style checks under `tests/`:

- `tests/test_final_answer.py` runs a single end-to-end question.
- `tests/test_agent_logic.py` checks a positive and negative query.
- `tests/test_agent_traces.py` prints the final graph state.
- `tests/test_multiple_files.py` checks file-specific filtering.

Run them with Poetry:

```bash
poetry run python tests/test_final_answer.py
poetry run python tests/test_agent_logic.py
poetry run python tests/test_agent_traces.py
poetry run python tests/test_multiple_files.py
```

## Model Configuration

The current default embedding and chat model is `qwen2.5:3b` via Ollama. If you change the model, update the comments and README so they match the code.

## Notes

- Generated PDFs and Qdrant storage are intentionally ignored in Git.
- The repository uses `dev` for active implementation work.
