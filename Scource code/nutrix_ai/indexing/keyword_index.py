import sqlite3
import json
import logging

logger = logging.getLogger(__name__)

class KeywordIndex:
    """
    Keyword index using SQLite3 FTS5 (Full-Text Search) for fast lexical retrieval.
    """
    def __init__(self, db_path="nutrix_web_index.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # We create a standard table to hold metadata and full content
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                url TEXT,
                canonical_url TEXT,
                title TEXT,
                domain TEXT,
                category TEXT,
                authority_score REAL,
                published_at TEXT,
                updated_at TEXT,
                crawled_at TEXT,
                content TEXT,
                source_type TEXT,
                is_mock BOOLEAN,
                is_verified BOOLEAN
            )
        ''')
        
        # We create an FTS5 virtual table for keyword search
        # We use standard tokenizer
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                id UNINDEXED, 
                title, 
                content,
                tokenize="porter"
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_document(self, doc_id, document_data):
        """Add a document to the index."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert into main table
            cursor.execute('''
                INSERT OR REPLACE INTO documents 
                (id, url, canonical_url, title, domain, category, authority_score, 
                 published_at, updated_at, crawled_at, content, source_type, is_mock, is_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_id,
                document_data.get('url', ''),
                document_data.get('canonical_url', ''),
                document_data.get('title', ''),
                document_data.get('domain', ''),
                document_data.get('category', 'general'),
                document_data.get('authority_score', 1.0),
                document_data.get('published_at', ''),
                document_data.get('updated_at', ''),
                document_data.get('crawled_at', ''),
                document_data.get('content', ''),
                document_data.get('source_type', 'other'),
                1 if document_data.get('is_mock', False) else 0,
                1 if document_data.get('is_verified', True) else 0
            ))
            
            # Insert into FTS table
            # First delete existing if replacing
            cursor.execute('DELETE FROM documents_fts WHERE id = ?', (doc_id,))
            
            cursor.execute('''
                INSERT INTO documents_fts (id, title, content)
                VALUES (?, ?, ?)
            ''', (
                doc_id,
                document_data.get('title', ''),
                document_data.get('content', '')
            ))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error adding document to keyword index: {e}")
            conn.rollback()
        finally:
            conn.close()

    def search(self, query, top_k=10):
        """Search the keyword index using FTS5 match and return basic bm25 ranking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Prepare FTS query by cleaning it
        clean_query = query.replace('"', '').replace("'", "")
        # Remove small words to avoid FTS stopword issues
        words = [w for w in clean_query.split() if len(w) > 3]
        
        if not words:
            conn.close()
            return []
            
        # Use OR between words, but enclose each word in quotes to prevent FTS5 syntax errors with reserved words
        fts_query = ' OR '.join([f'"{w}"' for w in words])
        
        results = []
        try:
            cursor.execute('''
                SELECT d.id, d.title, d.url, d.domain, d.authority_score, 
                       d.published_at, d.content, bm25(documents_fts) as rank,
                       d.source_type, d.is_mock, d.is_verified
                FROM documents_fts f
                JOIN documents d ON f.id = d.id
                WHERE documents_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            ''', (fts_query, top_k))
            
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'title': row[1],
                    'url': row[2],
                    'domain': row[3],
                    'authority_score': row[4],
                    'published_at': row[5],
                    'content': row[6],
                    'keyword_score': abs(row[7]),
                    'source_type': row[8],
                    'is_mock': bool(row[9]),
                    'is_verified': bool(row[10])
                })
        except Exception as e:
            logger.error(f"FTS5 Search error: {e}")
            
        # If FTS5 didn't find anything, try LIKE fallback
        if not results:
            try:
                # We'll just search for the first substantive word using LIKE
                fallback_term = words[0] if words else "nutrition"
                like_q = f"%{fallback_term}%"
                
                cursor.execute('''
                    SELECT id, title, url, domain, authority_score, 
                           published_at, content, source_type, is_mock, is_verified
                    FROM documents
                    WHERE title LIKE ? OR content LIKE ?
                    LIMIT ?
                ''', (like_q, like_q, top_k))
                
                for row in cursor.fetchall():
                    results.append({
                        'id': row[0],
                        'title': row[1],
                        'url': row[2],
                        'domain': row[3],
                        'authority_score': row[4],
                        'published_at': row[5],
                        'content': row[6],
                        'keyword_score': 1.0, # arbitrary fallback score
                        'source_type': row[7],
                        'is_mock': bool(row[8]),
                        'is_verified': bool(row[9])
                    })
            except Exception as e2:
                logger.error(f"Fallback search error: {e2}")
        
        conn.close()
        return results

    def get_document(self, doc_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = ['id', 'url', 'canonical_url', 'title', 'domain', 'category', 
                       'authority_score', 'published_at', 'updated_at', 'crawled_at', 
                       'content', 'source_type', 'is_mock', 'is_verified']
            doc_dict = dict(zip(columns, row))
            doc_dict['is_mock'] = bool(doc_dict['is_mock'])
            doc_dict['is_verified'] = bool(doc_dict['is_verified'])
            return doc_dict
        return None
