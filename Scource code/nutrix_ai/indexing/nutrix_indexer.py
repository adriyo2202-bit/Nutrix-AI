import hashlib
import re
import logging
from .keyword_index import KeywordIndex
from .vector_store import VectorStore

logger = logging.getLogger(__name__)

class NutrixIndexer:
    """
    Coordinates chunking and inserting documents into both the 
    keyword index and the vector store.
    """
    def __init__(self, keyword_db_path="nutrix_web_index.db", vector_db_path="nutrix_vectors.db"):
        self.keyword_index = KeywordIndex(db_path=keyword_db_path)
        self.vector_store = VectorStore(db_path=vector_db_path)

    def _generate_doc_id(self, url):
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def _chunk_text(self, text, max_tokens=600, overlap=100):
        """
        Simple structure-aware chunking based on paragraphs.
        (Assuming 1 token ~ 4 characters roughly for english)
        """
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
                
            p_len = len(p) // 4 # rough token estimate
            
            if current_length + p_len > max_tokens and current_chunk:
                # Save current chunk
                chunk_text = "\n\n".join(current_chunk)
                chunks.append(chunk_text)
                
                # Start new chunk with overlap (keep last paragraph if fits)
                # For simplicity, we just keep the last paragraph as overlap if it's not too big
                if p_len < overlap:
                    current_chunk = [p]
                    current_length = p_len
                else:
                    current_chunk = [p]
                    current_length = p_len
            else:
                current_chunk.append(p)
                current_length += p_len
                
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
            
        return chunks

    def index_web_document(self, document_data):
        """Index a crawled web page."""
        url = document_data.get('url')
        if not url:
            logger.error("Document has no URL. Cannot index.")
            return False
            
        doc_id = self._generate_doc_id(url)
        logger.info(f"Indexing web document: {url} (ID: {doc_id})")
        
        # 1. Add to keyword index (full document)
        self.keyword_index.add_document(doc_id, document_data)
        
        # 2. Add to vector index (chunked)
        content = document_data.get('content', '')
        chunks = self._chunk_text(content)
        
        # Clear existing chunks for this doc before re-adding
        self.vector_store.delete_document(doc_id)
        
        for i, chunk in enumerate(chunks):
            self.vector_store.add_chunk(doc_id, i, chunk)
            
        return True
