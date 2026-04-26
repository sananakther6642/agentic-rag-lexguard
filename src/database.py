import os
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Local embedding model used for document indexing and retrieval.
embeddings = OllamaEmbeddings(model="qwen2.5:3b")

# Qdrant connection settings.
URL = "http://localhost:6333"
COLLECTION_NAME = "lexguard_docs"

def process_document(file_path: str):
    try:
        loader = PyPDFLoader(file_path)
        raw_docs = loader.load()
        file_name = os.path.basename(file_path)
        total_pages = len(raw_docs)
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1100,
            chunk_overlap=150,
            separators=["\n\n", "\n", "•", " ", ""]
        )
        
        all_chunks = []
        for i, page in enumerate(raw_docs):
            page_chunks = splitter.split_documents([page])
            for chunk in page_chunks:
                chunk.metadata["source_file"] = file_name
                chunk.metadata["page_label"] = i + 1
            
            all_chunks.extend(page_chunks)
            yield int((i + 1) / total_pages * 100), None

        QdrantVectorStore.from_documents(
            all_chunks,
            embeddings,
            url=URL,
            collection_name=COLLECTION_NAME,
            force_recreate=True
        )
        yield 100, len(all_chunks)
    except Exception as e:
        yield 0, str(e)

def search_knowledge(query: str, filter_file: str = None, k: int = 10):
    """
    Perform vector similarity search with optional file-based filtering.
    """
    client = QdrantClient(url=URL)
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings
    )
    
    from qdrant_client import models
    qdrant_filter = None
    if filter_file:
        qdrant_filter = models.Filter(
            must=[models.FieldCondition(key="metadata.source_file", match=models.MatchValue(value=filter_file))]
        )

    return vector_store.similarity_search(query, k=k, filter=qdrant_filter)

