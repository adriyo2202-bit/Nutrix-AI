import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nutrix_ai.core.nutrix_intelligence import NutrixIntelligence
from nutrix_ai.cli_test import seed_test_data

def run_tests():
    # Clean databases
    for db in ["nutrix_rag.db", "nutrix_rag_vectors.db", "nutrix_web.db", "nutrix_web_vectors.db"]:
        if os.path.exists(db):
            os.remove(db)
            
    print("Initializing Nutrix Intelligence Layer for Testing...")
    intelligence = NutrixIntelligence()
    seed_test_data(intelligence)
    
    # Custom Seed for specific tests (Stale, Authority, Fake URL)
    # 5. Stale Web Index
    old_date = (datetime.now() - timedelta(days=365 * 5)).isoformat()
    intelligence.web_indexer.index_web_document({
        'url': 'https://fssai.gov.in/old-guideline',
        'title': 'Old FSSAI Guidelines',
        'content': 'These guidelines are from 5 years ago.',
        'published_at': old_date,
        'source_type': 'government',
        'is_mock': False,
        'is_verified': True
    })
    
    # 6. Fake URL Protection
    intelligence.web_indexer.index_web_document({
        'url': 'https://fake-url.com/guideline',
        'title': 'Fake FSSAI Guidelines',
        'content': 'This is fake information to test mock hiding.',
        'published_at': datetime.now().isoformat(),
        'source_type': 'government',
        'is_mock': True, # MUST HIDE URL
        'is_verified': False
    })
    
    # 7. Authority
    intelligence.web_indexer.index_web_document({
        'url': 'https://random-blog.com/food-additive',
        'title': 'Is INS 621 safe?',
        'content': 'I think INS 621 is bad for you.',
        'published_at': datetime.now().isoformat(),
        'source_type': 'blog',
        'is_mock': False,
        'is_verified': True
    })
    intelligence.web_indexer.index_web_document({
        'url': 'https://fssai.gov.in/ins-621',
        'title': 'INS 621 Official Safety',
        'content': 'INS 621 is generally recognized as safe under specified limits.',
        'published_at': datetime.now().isoformat(),
        'source_type': 'government',
        'is_mock': False,
        'is_verified': True
    })
    
    tests = [
        ("Test 1 - Stable Knowledge", "What is protein?", "user_A"),
        ("Test 2 - Personal Data", "How much protein have I eaten today?", "user_A"),
        ("Test 3 - Personalized Rec", "What should I eat tonight?", "user_A"),
        ("Test 4/5 - Current Info & Stale Fallback", "What are the latest FSSAI guidelines for trans fats?", "user_A"),
        ("Test 6 - Fake URL Protection", "Tell me about the fake guidelines", "user_A"),
        ("Test 7 - Authority", "Is food additive INS 621 safe according to authorities?", "user_A"),
        ("Test 8 - Protein Caution", "I have 14g protein left. Should I drink a 25g whey protein shake?", "user_A"),
        ("Test 9 - Privacy B", "How much protein have I eaten today?", "user_B"),
        ("Test 10 - Insufficient Info", "What is the newly discovered vitamin X49 and its guidelines for 2027?", "user_A"),
    ]
    
    for test_name, query, user_id in tests:
        print(f"\n{'='*60}")
        print(f"[{test_name}] USER ({user_id}): {query}")
        print(f"{'='*60}")
        print("NUTRIX AI:")
        
        for chunk in intelligence.handle_query(query, user_id=user_id):
            print(chunk, end="", flush=True)
        print("\n")

if __name__ == "__main__":
    run_tests()
