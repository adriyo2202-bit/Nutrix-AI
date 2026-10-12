from datetime import datetime
import dateutil.parser

class Reranker:
    """
    Reranks documents based on Relevance, Authority, Freshness, and Intent match.
    """
    def __init__(self, weights=None):
        if weights is None:
            self.weights = {
                'relevance': 0.5,
                'authority': 0.3,
                'freshness': 0.2
            }
        else:
            self.weights = weights

    def _calculate_freshness_score(self, published_at_str, intent_tags):
        """
        Calculate freshness score. If intent includes 'CURRENT_INFORMATION',
        freshness decays much faster and matters more.
        """
        if not published_at_str:
            return 0.5 # Neutral if no date provided
            
        try:
            pub_date = dateutil.parser.parse(published_at_str).replace(tzinfo=None)
            now = datetime.utcnow()
            days_old = (now - pub_date).days
            
            if days_old < 0:
                return 1.0 # Future dates? Cap at 1.0
                
            # If current info is needed, decay quickly (e.g. half-life of 30 days)
            if 'CURRENT_INFORMATION' in intent_tags:
                score = 1.0 / (1.0 + (days_old / 30.0))
            else:
                # Stable info decays slowly (e.g. half-life of 1000 days)
                score = 1.0 / (1.0 + (days_old / 1000.0))
                
            return max(0.1, score) # floor at 0.1
        except Exception:
            return 0.5

    def rerank(self, candidates, intent_tags, top_k=5):
        """
        Candidates should be a list of dictionaries with:
        keyword_relevance, vector_relevance, authority_score, published_at, source_type
        """
        # Adjust weights dynamically based on intent
        current_weights = self.weights.copy()
        if 'CURRENT_INFORMATION' in intent_tags:
            current_weights['freshness'] = 0.4
            current_weights['relevance'] = 0.4
            current_weights['authority'] = 0.2
        elif 'STABLE_KNOWLEDGE' in intent_tags:
            current_weights['freshness'] = 0.05
            current_weights['relevance'] = 0.65
            current_weights['authority'] = 0.3
            
        reranked = []
        max_freshness_for_current = 0.0
        
        for doc in candidates:
            # Base relevance is max or average of keyword and vector? Let's use average
            relevance_score = (doc.get('keyword_relevance', 0.0) + doc.get('vector_relevance', 0.0)) / 2.0
            
            authority_score = doc.get('authority_score', 0.5)
            source_type = doc.get('source_type', 'other')
            
            # Boost authority for specific intents based on source_type
            if 'FOOD_SAFETY' in intent_tags and source_type in ['government', 'scientific', 'official_organization']:
                authority_score = min(1.0, authority_score + 0.3)
            elif 'RESEARCH' in intent_tags and source_type in ['scientific', 'academic']:
                authority_score = min(1.0, authority_score + 0.3)
            elif 'NUTRITION' in intent_tags and source_type == 'government':
                authority_score = min(1.0, authority_score + 0.2)
            
            freshness_score = self._calculate_freshness_score(doc.get('published_at', ''), intent_tags)
            
            if 'CURRENT_INFORMATION' in intent_tags:
                if freshness_score > max_freshness_for_current:
                    max_freshness_for_current = freshness_score
            
            final_score = (
                (relevance_score * current_weights['relevance']) +
                (authority_score * current_weights['authority']) +
                (freshness_score * current_weights['freshness'])
            )
            
            doc['final_score'] = final_score
            reranked.append(doc)
            
        reranked.sort(key=lambda x: x['final_score'], reverse=True)
        
        is_stale = False
        if 'CURRENT_INFORMATION' in intent_tags and max_freshness_for_current < 0.4:
            is_stale = True
            
        return {
            'results': reranked[:top_k],
            'is_stale': is_stale
        }
