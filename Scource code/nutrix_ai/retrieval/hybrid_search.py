class HybridSearch:
    """
    Combines Keyword and Semantic search results and deduplicates them.
    """
    def __init__(self, keyword_index, vector_store):
        self.keyword_index = keyword_index
        self.vector_store = vector_store

    def search(self, query, top_k=20):
        # 1. Get Keyword Results (returns document-level results)
        kw_results = self.keyword_index.search(query, top_k=top_k)
        
        # 2. Get Vector Results (returns chunk-level results)
        vec_results = self.vector_store.search(query, top_k=top_k)
        
        # 3. Merge and deduplicate
        merged_candidates = {}
        
        # Process Keyword results (normalize scores roughly)
        max_kw_score = max([r['keyword_score'] for r in kw_results]) if kw_results else 1.0
        if max_kw_score == 0: max_kw_score = 1.0
        
        for r in kw_results:
            doc_id = r['id']
            merged_candidates[doc_id] = {
                'doc_id': doc_id,
                'title': r['title'],
                'url': r['url'],
                'domain': r['domain'],
                'authority_score': r['authority_score'],
                'published_at': r['published_at'],
                'source_type': r.get('source_type', 'other'),
                'is_mock': r.get('is_mock', False),
                'is_verified': r.get('is_verified', True),
                'content': r['content'], # Full content might be too big, we might want just chunks later
                'keyword_relevance': r['keyword_score'] / max_kw_score,
                'vector_relevance': 0.0 # Will be updated if found in vector search
            }
            
        # Process Vector results
        max_vec_score = max([r['vector_score'] for r in vec_results]) if vec_results else 1.0
        if max_vec_score == 0: max_vec_score = 1.0
        
        for r in vec_results:
            doc_id = r['doc_id']
            normalized_vec_score = r['vector_score'] / max_vec_score
            
            if doc_id in merged_candidates:
                # Update vector score if it's higher than existing
                merged_candidates[doc_id]['vector_relevance'] = max(
                    merged_candidates[doc_id]['vector_relevance'], 
                    normalized_vec_score
                )
            else:
                # Need to fetch doc metadata from keyword index (which acts as doc store)
                doc_meta = self.keyword_index.get_document(doc_id)
                if doc_meta:
                    merged_candidates[doc_id] = {
                        'doc_id': doc_id,
                        'title': doc_meta['title'],
                        'url': doc_meta['url'],
                        'domain': doc_meta['domain'],
                        'authority_score': doc_meta['authority_score'],
                        'published_at': doc_meta['published_at'],
                        'source_type': doc_meta.get('source_type', 'other'),
                        'is_mock': doc_meta.get('is_mock', False),
                        'is_verified': doc_meta.get('is_verified', True),
                        # We use the specific chunk that matched well, or the whole content
                        'content': r['content'], 
                        'keyword_relevance': 0.0,
                        'vector_relevance': normalized_vec_score
                    }
                    
        return list(merged_candidates.values())
