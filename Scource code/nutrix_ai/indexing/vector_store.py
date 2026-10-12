import logging
import chromadb

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Local vector store using ChromaDB for persistence and high-performance embedding search.
    This completely replaces the naive SQLite implementation and uses completely local embeddings.
    """
    def __init__(self, db_path="nutrix_vectors.db"):
        self.db_path = db_path
        
        # We use a single persistent directory for ChromaDB (ABSOLUTE PATH FIX)
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        client_path = os.path.join(base_dir, "chroma_data")
        
        # Map the old SQLite db_path to a Chroma collection name (e.g. nutrix-rag-vectors)
        coll_name = db_path.replace(".db", "").replace("_", "-")
        
        try:
            self.client = chromadb.PersistentClient(path=client_path)
            # By default, Chroma uses all-MiniLM-L6-v2 which runs 100% locally on CPU.
            self.collection = self.client.get_or_create_collection(name=coll_name)
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")

    def add_chunk(self, doc_id, chunk_index, content):
        """Generate local embedding and store a document chunk."""
        chunk_id = f"{doc_id}_{chunk_index}"
        
        try:
            self.collection.upsert(
                documents=[content],
                metadatas=[{"doc_id": doc_id, "chunk_index": chunk_index}],
                ids=[chunk_id]
            )
            return True
        except Exception as e:
            logger.error(f"Error adding chunk to ChromaDB: {e}")
            return False

    def delete_document(self, doc_id):
        try:
            self.collection.delete(where={"doc_id": doc_id})
        except Exception as e:
            logger.error(f"Error deleting from ChromaDB: {e}")

    def search(self, query, top_k=10):
        """Search by embedding similarity."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            scores = []
            if results and results.get('ids') and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    chunk_id = results['ids'][0][i]
                    metadata = results['metadatas'][0][i]
                    content = results['documents'][0][i]
                    distance = results['distances'][0][i]
                    
                    # Convert L2 distance to a similarity score (lower distance = higher similarity)
                    similarity_score = 1.0 / (1.0 + distance)
                    
                    scores.append({
                        'chunk_id': chunk_id,
                        'doc_id': metadata.get('doc_id', ''),
                        'content': content,
                        'vector_score': similarity_score
                    })
            return scores
        except Exception as e:
            logger.error(f"Chroma search error: {e}")
            return []

