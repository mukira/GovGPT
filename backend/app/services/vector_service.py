"""
Vector Service
Manages document embeddings and semantic search using Qdrant
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import hashlib


class VectorService:
    """Qdrant vector database service for document retrieval"""
    
    def __init__(self, qdrant_url: str = None, qdrant_key: str = None):
        """
        Initialize vector service
        
        Args:
            qdrant_url: Qdrant cloud URL
            qdrant_key: Qdrant API key
        """
        self.qdrant_url = qdrant_url
        self.qdrant_key = qdrant_key
        self.client = None
        self.embeddings_model = None
        self.collection_name = "govgpt_documents"
        self.vector_size = 384  # all-MiniLM-L6-v2 dimension
        
        if qdrant_url and qdrant_key:
            self._initialize()
    
    def _initialize(self):
        """Initialize Qdrant client and embeddings model"""
        try:
            # Connect to Qdrant
            self.client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_key,
            )
            
            # Load embeddings model
            print("Loading embeddings model...")
            self.embeddings_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
            # Create collection if it doesn't exist
            self._ensure_collection()
            
            print("✅ Vector service initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize vector service: {e}")
            raise
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Created collection: {self.collection_name}")
            
        except Exception as e:
            print(f"Error creating collection: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if not self.embeddings_model:
            raise Exception("Embeddings model not initialized")
        
        embedding = self.embeddings_model.encode(text)
        return embedding.tolist()
    
    def store_chunks(self, chunks: List[Dict], document_id: str):
        """
        Store document chunks in Qdrant
        
        Args:
            chunks: List of text chunks with metadata
            document_id: Unique document identifier
        """
        if not self.client:
            raise Exception("Qdrant client not initialized")
        
        points = []
        
        for chunk in chunks:
            # Generate embedding
            embedding = self.embed_text(chunk['text'])
            
            # Create unique point ID
            point_id = hashlib.md5(
                f"{document_id}_{chunk['chunk_id']}".encode()
            ).hexdigest()[:16]
            
            # Create point
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    'document_id': document_id,
                    'chunk_id': chunk['chunk_id'],
                    'text': chunk['text'],
                    'filename': chunk.get('filename', ''),
                    'type': chunk.get('type', ''),
                    'start': chunk.get('start', 0),
                    'end': chunk.get('end', 0)
                }
            )
            points.append(point)
        
        # Upload in batches of 100
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
        
        print(f"✅ Stored {len(points)} chunks for document {document_id}")
    
    def search_similar(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for similar chunks
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            List of similar chunks with scores
        """
        if not self.client or not self.embeddings_model:
            raise Exception("Vector service not initialized")
        
        # Generate query embedding
        query_embedding = self.embed_text(query)
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit
        )
        
        # Format results
        similar_chunks = []
        for result in results:
            similar_chunks.append({
                'text': result.payload['text'],
                'filename': result.payload['filename'],
                'document_id': result.payload['document_id'],
                'chunk_id': result.payload['chunk_id'],
                'score': result.score
            })
        
        return similar_chunks
    
    def delete_document(self, document_id: str):
        """Delete all chunks for a document"""
        if not self.client:
            raise Exception("Qdrant client not initialized")
        
        self.client.delete(
            collection_name=self.collection_name,
            points_selector={
                "filter": {
                    "must": [
                        {
                            "key": "document_id",
                            "match": {"value": document_id}
                        }
                    ]
                }
            }
        )
        print(f"✅ Deleted chunks for document {document_id}")


# Singleton instance (will be initialized with credentials from config)
vector_service = VectorService()
