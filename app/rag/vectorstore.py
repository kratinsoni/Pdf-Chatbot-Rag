# vectorstore.py
from langchain_qdrant import QdrantVectorStore
from langchain_cohere import CohereEmbeddings
from dotenv import load_dotenv
from typing import List
from langchain_core.documents import Document
from qdrant_client.models import Filter, FieldCondition, MatchValue




load_dotenv()

embedder = CohereEmbeddings(model="embed-english-v3.0")

vector_store = QdrantVectorStore.from_existing_collection(
    url="http://qdrant:6333",
    collection_name="PDF_CONTEXT",
    embedding=embedder
)


def get_relevant_chunks(file_id: str, query: str) -> List[Document]:
    
    filter = Filter(
        must=[
            FieldCondition(
                key="file_id",
                match=MatchValue(value=file_id)
            )
        ]
    )
    
    return vector_store.similarity_search(
        query=query,
        k=5,
        filter=filter  # Qdrant filtering
    )
