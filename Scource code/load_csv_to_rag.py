import sys
import os
import pandas as pd

# Add parent directory to path so we can import nutrix_ai
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nutrix_ai.core.nutrix_intelligence import NutrixIntelligence
import logging

logging.basicConfig(level=logging.INFO)

def load_csv_to_rag():
    print("Initializing Nutrix Intelligence Layer...")
    intelligence = NutrixIntelligence()
    
    csv_file = "ifct_data.csv"
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        return

    print(f"Loading {csv_file}...")
    df = pd.read_csv(csv_file)
    
    count = 0
    for index, row in df.iterrows():
        name = row.get("name", "Unknown Food")
        calories = row.get("calories", 0)
        protein = row.get("protein_g", 0)
        carbs = row.get("carbs_g", 0)
        fats = row.get("fat_g", 0)
        allergens = row.get("allergens", "None")
        
        # Format the chunk to explicitly contain nutrient values
        content = (
            f"Nutritional profile for {name}:\n"
            f"- Calories: {calories} kcal\n"
            f"- Protein: {protein} g\n"
            f"- Carbohydrates: {carbs} g\n"
            f"- Fat: {fats} g\n"
            f"- Allergens: {allergens if allergens and str(allergens) != 'nan' else 'None'}\n"
        )
        
        document_data = {
            "url": f"internal://nutrition/ifct/{name.replace(' ', '_').lower()}",
            "title": name,
            "content": content,
            "category": "NUTRITION_FACTS"
        }
        
        # Load the document into ChromaDB
        intelligence.rag_indexer.index_web_document(document_data)
        count += 1
        
    print(f"\n✓ Successfully embedded {count} food items from CSV into ChromaDB!")

if __name__ == "__main__":
    load_csv_to_rag()
