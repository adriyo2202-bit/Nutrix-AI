import sys
import os

# Add parent directory to path so we can import nutrix_ai
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nutrix_ai.core.nutrix_intelligence import NutrixIntelligence
import logging

logging.basicConfig(level=logging.WARNING)

def seed_test_data(intelligence):
    """Seed the RAG and Web index with some dummy data for testing."""
    print("Seeding test data...")
    
    # 1. Seed RAG
    rag_doc = {
        "url": "internal://nutrition/protein",
        "title": "Protein Basics",
        "content": "Protein is an essential macronutrient needed by the human body for growth and maintenance. It is found in animal products like meat and dairy, and plant sources like lentils, tofu, and nuts. The recommended daily allowance is generally 0.8g per kg of body weight for an average sedentary adult.",
        "category": "NUTRITION",
    }
    intelligence.rag_indexer.index_web_document(rag_doc)
    
    # 2. Seed Web
    web_doc_1 = {
        "url": "https://fssai.gov.in/latest-guideline",
        "title": "FSSAI Latest Trans Fat Guideline",
        "domain": "fssai.gov.in",
        "category": "food_safety",
        "authority_score": 1.0,
        "published_at": "2026-01-15T00:00:00Z",
        "content": "The Food Safety and Standards Authority of India (FSSAI) has updated its guidelines in early 2026, restricting trans fats in all oils and fats to not more than 2% by weight."
    }
    web_doc_2 = {
        "url": "https://nih.gov/research/protein-2026",
        "title": "Recent Research on High-Protein Diets",
        "domain": "nih.gov",
        "category": "research",
        "authority_score": 0.95,
        "published_at": "2026-05-20T00:00:00Z",
        "content": "A recent 2026 study suggests that consuming up to 1.6g of protein per kg of body weight is safe and beneficial for muscle recovery in active individuals. There is no evidence of kidney damage in healthy adults."
    }
    intelligence.web_indexer.index_web_document(web_doc_1)
    intelligence.web_indexer.index_web_document(web_doc_2)
    print("Test data seeded.\n")

def main():
    print("=======================================")
    print(" NUTRIX AI INTELLIGENCE LAYER - CLI TEST")
    print("=======================================\n")
    
    intelligence = NutrixIntelligence()
    seed_test_data(intelligence)
    
    print("Users available: 'user_A' (High Protein), 'user_B' (Weight Loss)")
    user_id = input("Select user [default: user_A]: ").strip()
    if not user_id:
        user_id = "user_A"
        
    print(f"\nWelcome {user_id}!")
    print("Type your questions below. Type 'exit' to quit.")
    print("Commands:")
    print("  /scan  - Simulate Health Lens scanning a meal")
    print("  /clear - Clear chat history\n")
    
    while True:
        try:
            query = input("\nYou: ").strip()
            
            if query.lower() in ['exit', 'quit']:
                print("\nNutrix: Stay healthy! Goodbye.")
                break
                
            if query.lower() == '/clear':
                intelligence.chat_history = []
                print("[Chat history cleared]")
                continue
                
            if query.lower() == '/scan':
                print("[Simulating Health Lens...]")
                intelligence.user_context_svc.set_health_lens_context({
                    "Food": "Chicken Biryani",
                    "Calories": "640 kcal",
                    "Protein": "28g",
                    "Carbs": "72g",
                    "Fat": "24g",
                    "Safety Note": "High sodium"
                })
                print("[Health Lens context loaded! Try asking 'Is this good for me?']")
                continue
                
            if not query:
                continue
                
            print("Nutrix: ", end="", flush=True)
            
            # Generator yields chunks and then potentially a sources string at the end
            for chunk in intelligence.handle_query(query, user_id=user_id):
                print(chunk, end="", flush=True)
                
            print()
            
            # Clear health lens after a query to simulate typical usage, unless they want to keep asking about it
            # But let's leave it for now to allow follow-ups.
            
        except KeyboardInterrupt:
            print("\n\nNutrix: Goodbye!")
            break
        except Exception as e:
            print(f"\n[Error]: {e}")

if __name__ == "__main__":
    main()
