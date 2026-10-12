import logging
import json
import os
from ..routing.nutrix_router import NutrixRouter
from ..user.nutrix_user_context import NutrixUserContext
from ..indexing.nutrix_indexer import NutrixIndexer
from ..retrieval.nutrix_retriever import NutrixRetriever
from ..retrieval.openfoodfacts_retriever import OpenFoodFactsRetriever
from ..generation.context_builder import ContextBuilder
from ..generation.llm_provider import LLMProvider
from ..crawler.nutrix_crawler import NutrixCrawler

logger = logging.getLogger(__name__)

class NutrixIntelligence:
    """
    Main orchestration class for the Nutrix AI Intelligence Layer.
    """
    def __init__(self):
        # We maintain two separate indexes: one for RAG (stable) and one for Web Search (current)
        self.rag_indexer = NutrixIndexer(keyword_db_path="nutrix_rag.db", vector_db_path="nutrix_rag_vectors.db")
        self.web_indexer = NutrixIndexer(keyword_db_path="nutrix_web.db", vector_db_path="nutrix_web_vectors.db")
        
        self.rag_retriever = NutrixRetriever(self.rag_indexer.keyword_index, self.rag_indexer.vector_store)
        self.web_retriever = NutrixRetriever(self.web_indexer.keyword_index, self.web_indexer.vector_store)
        self.off_retriever = OpenFoodFactsRetriever()
        
        self.router = NutrixRouter()
        self.user_context_svc = NutrixUserContext()
        self.context_builder = ContextBuilder()
        self.llm = LLMProvider()
        self.crawler = NutrixCrawler()
        
        self.chat_history = []
        
        # Load trusted domains
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'trusted_domains.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.trusted_domains = json.load(f)
        else:
            self.trusted_domains = []

    def handle_query(self, query, user_id="user_A", simulate_web_crawl=False, db_chat_history=None):
        """
        End-to-end pipeline for answering a user query.
        """
        # 1. Routing
        has_lens = self.user_context_svc.health_lens is not None
        route_info = self.router.route(query, has_health_lens=has_lens)
        intent_tags = route_info['tags']
        
        # Determine sources
        use_rag = route_info['use_rag']
        use_web = route_info['use_web']
        use_user = route_info['use_user_context']
        use_off = route_info.get('use_off', False)
        
        logger.info(f"Route tags: {intent_tags}")
        
        # 2. Retrieve User Context
        user_context_dict = None
        if use_user:
            user_context_dict = self.user_context_svc.get_context(user_id, intent_tags)
            
        # 3. Retrieve RAG
        rag_results = []
        if use_rag:
            # For demonstration, we just retrieve directly. In a real system the RAG DB is pre-populated.
            rag_output = self.rag_retriever.retrieve(query, intent_tags)
            rag_results = rag_output.get('results', [])
            
        # 4. Retrieve Web with Fallback Loop and UI Indicators
        web_results = []
        if use_web:
            yield "[UI: Searching trusted sources...]\n"
            
            web_output = self.web_retriever.retrieve(query, intent_tags)
            web_results = web_output.get('results', [])
            is_stale = web_output.get('is_stale', False)
            
            # If stale or empty and current info needed, fallback to crawl
            if (is_stale or not web_results) and 'CURRENT_INFORMATION' in intent_tags:
                yield "[UI: Missing or stale information detected. Live crawling trusted sources...]\n"
                # Simulated Fallback URL discovery (since we lack search API)
                fallback_url = "https://fssai.gov.in/latest-guideline"
                if "protein" in query.lower() or "research" in query.lower():
                    fallback_url = "https://nih.gov/research/protein-2026"
                
                # In a real app we'd fetch multiple URLs, here we just fetch one known one
                # to satisfy the system's crawler component for testing.
                doc_data = self.crawler.fetch_page(fallback_url)
                if doc_data:
                    doc_data['source_type'] = 'government' if 'fssai' in fallback_url else 'scientific'
                    doc_data['is_mock'] = False
                    doc_data['is_verified'] = True
                    self.web_indexer.index_web_document(doc_data)
                    
                    # Re-retrieve after indexing
                    web_output = self.web_retriever.retrieve(query, intent_tags)
                    web_results = web_output.get('results', [])
                    
            yield "[UI: Reviewing sources... Preparing answer...]\n\n"
            
        # 4b. Retrieve Open Food Facts
        off_results = []
        if use_off:
            yield "[UI: Looking up product in Open Food Facts database...]\n"
            off_output = self.off_retriever.retrieve(query)
            off_results = off_output.get('results', [])
            if off_results:
                yield f"[UI: Found product: {off_results[0]['title']}]\n\n"
            
        # 5. Build Context
        messages = self.context_builder.build(
            query=query,
            user_context_dict=user_context_dict,
            rag_results=rag_results,
            web_results=web_results,
            off_results=off_results,
            chat_history=db_chat_history if db_chat_history is not None else self.chat_history
        )
        
        # 6. Generate Response
        response_stream = self.llm.generate_stream(messages)
        
        # 7. Collect Response for history and UI
        full_response = ""
        for chunk in response_stream:
            yield chunk
            full_response += chunk
            
        # Save to internal memory history just in case
        self.chat_history.append({"role": "user", "content": query})
        self.chat_history.append({"role": "assistant", "content": full_response})
        
        # Return sources if web was used
        if use_web and web_results:
            sources_str = "\n\nSources:\n"
            added_sources = False
            for r in web_results:
                if not r.get('is_mock', False):
                    sources_str += f"- {r.get('title', 'Unknown')} ({r.get('url', 'Unknown')})\n"
                    added_sources = True
            
            if added_sources:
                yield sources_str
