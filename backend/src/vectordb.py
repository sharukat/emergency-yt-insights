import os
import uuid
from tqdm import tqdm
from typing import List
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from src.global_settings import EMBED_MODEL

load_dotenv(dotenv_path=".env")


class VectorDB:
    def __init__(self) -> None:
        self.dense_embedding = OllamaEmbeddings(
            model=EMBED_MODEL, base_url=os.environ.get("OLLAMA_SERVICE")
        )
        self.sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

    def create_document(self, id: int, item: dict, field: str) -> Document:
        return Document(
            page_content=f"search_document: {item[field]}",
            metadata={
                "video_id": item["video_id"],
                "title": item["title"],
                "url": item["url"],
            },
            id=id,
        )

    def get_documents(self, data: List[dict]) -> List[Document]:
        documents = []
        for item in tqdm(data, total=len(data)):
            id = str(uuid.uuid4())
            documents.append(self.create_document(id, item, "text"))
        return documents

    def create_vectordb(self, records: List[dict], collection_name: str):
        try:
            documents = self.get_documents(records)
            QdrantVectorStore.from_documents(
                documents=documents,
                collection_name=collection_name,
                embedding=self.dense_embedding,
                sparse_embedding=self.sparse_embeddings,
                prefer_grpc=False,
                url=os.environ.get("QDRANT_SERVICE"),  # Connected to docker
                retrieval_mode=RetrievalMode.HYBRID,
            )
            print(f"{len(documents)} documents added to the vector store.")
        except Exception as e:
            raise e

    def add_to_exisitng_collection(self,
                                   records: List[dict],
                                   collection_name: str):
        try:
            documents = self.get_documents(records)
            qdrant = QdrantVectorStore.from_existing_collection(
                collection_name=collection_name,
                embedding=self.dense_embedding,
                sparse_embedding=self.sparse_embeddings,
                prefer_grpc=False,
                url=os.environ.get("QDRANT_SERVICE"),  # Connected to docker
                retrieval_mode=RetrievalMode.HYBRID,
            )
            qdrant.add_documents(documents=documents)
        except Exception as e:
            raise e
