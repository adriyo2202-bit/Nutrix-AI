import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nutrix_ai.core.nutrix_intelligence import NutrixIntelligence
from nutrix_ai.cli_test import seed_test_data

def main():
    print("Initializing Nutrix Intelligence Layer...")
    intelligence = NutrixIntelligence()
    
    # Clean databases for a fresh demo
    for db in ["nutrix_rag.db", "nutrix_rag_vectors.db", "nutrix_web.db", "nutrix_web_vectors.db"]:
        if os.path.exists(db):
            os.remove(db)
            
    # Re-initialize to recreate tables
    intelligence = NutrixIntelligence()
    
    seed_test_data(intelligence)
    
    queries = [
        ("What is protein?", "user_A"), # Should hit RAG
        ("What are the latest FSSAI guidelines for trans fats?", "user_A"), # Should hit Web
        ("What should I eat tonight? My goal is high protein.", "user_A"), # Should hit RAG + User Context
    ]
    
    for query, user_id in queries:
        print(f"\n{'='*50}")
        print(f"USER ({user_id}): {query}")
        print(f"{'='*50}")
        print("NUTRIX AI:")
        
        for chunk in intelligence.handle_query(query, user_id=user_id):
            print(chunk, end="", flush=True)
        print("\n")

if __name__ == "__main__":
    main()
