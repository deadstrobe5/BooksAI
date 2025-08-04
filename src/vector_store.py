from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.http import models
from openai import OpenAI
from config import (
    QDRANT_HOST,
    QDRANT_PORT,
    COLLECTION_NAME,
    OPENAI_API_KEY,
    EMBEDDING_MODEL
)

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure the collection exists with the correct settings."""
        collections = self.client.get_collections().collections
        exists = any(col.name == COLLECTION_NAME for col in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=1536,  # OpenAI embedding dimension
                    distance=models.Distance.COSINE
                )
            )

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text using OpenAI API."""
        response = self.openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding

    def add_documents(self, chunks: List[Dict[str, str]]):
        """Add documents to the vector store."""
        for i, chunk in enumerate(chunks):
            embedding = self._get_embedding(chunk["text"])
            
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    models.PointStruct(
                        id=i,
                        vector=embedding,
                        payload={
                            "text": chunk["text"],
                            **chunk["metadata"]
                        }
                    )
                ]
            )

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar documents."""
        query_embedding = self._get_embedding(query)
        
        results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit
        )
        
        return [
            {
                "text": result.payload["text"],
                "source": result.payload["source"],
                "chunk_index": result.payload["chunk_index"],
                "score": result.score
            }
            for result in results
        ]

    def print_all_chunks(self):
        """Print all chunks stored in the vector database."""
        try:
            # Get all points from the collection
            results = self.client.scroll(
                collection_name=COLLECTION_NAME,
                limit=100,  # Get all points (adjust if you have more)
                with_payload=True,
                with_vectors=False  # We don't need the vectors
            )[0]  # scroll returns (points, offset)
            
            print(f"\nTotal chunks found: {len(results)}")
            print("=" * 80 + "\n")
            
            for point in results:
                print(f"Chunk ID: {point.id}")
                print(f"Source: {point.payload['source']}")
                print(f"Chunk Index: {point.payload['chunk_index']}")
                print("-" * 40)
                print(point.payload['text'])
                print("\n" + "=" * 80 + "\n")
                
        except Exception as e:
            print(f"Error retrieving chunks: {str(e)}") 