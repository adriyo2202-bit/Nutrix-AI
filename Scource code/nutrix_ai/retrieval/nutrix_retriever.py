from .hybrid_search import HybridSearch
from .reranker import Reranker

import sqlite3
import os

class NutrixRetriever:
    """
    Main retrieval interface that combines HybridSearch, Reranking, and Direct Database Lookup.
    """
    def __init__(self, keyword_index, vector_store):
        self.hybrid_search = HybridSearch(keyword_index, vector_store)
        self.reranker = Reranker()
        self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'nutrix_rag.db')

    def retrieve(self, query, intent_tags, initial_k=20, final_k=5):
        """
        Retrieves documents based on query and intents.
        """
        # 1. Fetch Candidates (Hybrid)
        candidates = self.hybrid_search.search(query, top_k=initial_k)
        
        # 2. Rerank (returns dict with results and is_stale)
        rerank_output = self.reranker.rerank(candidates, intent_tags, top_k=final_k)
        
        # 3. Direct SQL Lookup for exact dataset matches
        db_results = self._sql_lookup(query)
        if db_results:
            rerank_output['results'] = db_results + rerank_output.get('results', [])
            
        return rerank_output

    def _sql_lookup(self, query):
        """Looks up exact matches in the ingested CSV SQLite tables."""
        if not os.path.exists(self.db_path):
            return []
            
        results = []
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check Ingredient Safety Rules
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ingredient_safety_rules'")
            if cursor.fetchone():
                words = query.lower().split()
                for word in words:
                    if len(word) > 3:
                        cursor.execute("SELECT * FROM ingredient_safety_rules WHERE LOWER(ingredient_name) LIKE ?", (f"%{word}%",))
                        rows = cursor.fetchall()
                        for row in rows:
                            content = f"Ingredient Safety Rule: {row['ingredient_name']} (E-Number: {row['ins_number']}). Status: {row['fssai_status']}. Flag: {row['overall_safety_flag']}. Health Risks: {row['primary_health_risks']}."
                            results.append({"content": content, "title": "Database: Ingredient Safety", "is_mock": False})

            # Check Food Consumption Stats
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='food_consumption_stats'")
            if cursor.fetchone():
                words = query.lower().split()
                for word in words:
                    if len(word) > 3:
                        cursor.execute("SELECT * FROM food_consumption_stats WHERE LOWER(FoodName) LIKE ? LIMIT 5", (f"%{word}%",))
                        rows = cursor.fetchall()
                        for row in rows:
                            content = f"Consumption Stat: {row['FoodName']} in {row['Country']} ({row['Year']}). Demographics: Age {row['AgeClass']}, Gender {row['Gender']}. Mean Consumers: {row['Consumers_Mean']}."
                            results.append({"content": content, "title": "Database: Food Consumption", "is_mock": False})
                            
            conn.close()
        except Exception as e:
            print(f"SQL Lookup Error: {e}")
            
        return results
