import os
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Setup Local Embeddings (Uses M3 GPU)
# Ensure you ran: ollama pull mistral-nemo
embeddings = OllamaEmbeddings(model="mistral-nemo")

# 2. Connect to Qdrant (Docker)
URL = "http://localhost:6333"
COLLECTION_NAME = "lexguard_docs"

def ingest_pdf(file_path: str):
    """
    Loads a PDF, splits it into chunks, and stores it in Qdrant.
    """
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    print(f"🚀 Processing: {file_path}")
    
    # Load and Split
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    
    # Recursive splitting preserves context better than simple splitting
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    
    print(f"📦 Created {len(chunks)} chunks. Generating embeddings...")

    # Upload to Qdrant
    QdrantVectorStore.from_documents(
        chunks,
        embeddings,
        url=URL,
        collection_name=COLLECTION_NAME,
        force_recreate=True # Start fresh for the first test
    )
    
    print("✅ Success! Data is now in Qdrant.")


def process_document(file_path: str):
    """Backward-compatible alias used by test scripts and older callers."""
    ingest_pdf(file_path)

def search_knowledge(query: str):
    """
    Search the 'Memory' (Qdrant) for the most relevant paragraphs.
    """
    # 1. Connect to the existing store
    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        url=URL,
    )
    
    # 2. Perform the search (k=3 means find the top 3 most relevant parts)
    results = vector_store.similarity_search(query, k=3)
    
    return results