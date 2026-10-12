import sys
import os
import pandas as pd
import logging
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nutrix_ai.core.nutrix_intelligence import NutrixIntelligence

logging.basicConfig(level=logging.INFO)

def load_massive_dataset():
    print("Initializing Nutrix Intelligence Layer...")
    intelligence = NutrixIntelligence()
    
    csv_file = "d:/project/fullcifocoss.csv"
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        return

    print("Loading 131MB Dataset (this may take a moment)...")
    # Using ; as delimiter based on file inspection
    df = pd.read_csv(csv_file, sep=";", low_memory=False)
    
    # 600,000+ rows is too large to embed raw on a local CPU. 
    # We will group by FoodName and summarize the consumption data 
    # to create a dense, highly informative Knowledge Base of unique foods.
    print(f"Original dataset size: {len(df)} rows.")
    
    print("Summarizing data by FoodName to optimize embedding...")
    # Clean up column names and numeric data
    df['Total_Mean'] = pd.to_numeric(df['Total_Mean'], errors='coerce').fillna(0)
    
    summary_df = df.groupby('FoodName').agg({
        'Country': lambda x: ', '.join(set(x.dropna())),
        'Total_Mean': 'mean',
        'FoodCode': 'first'
    }).reset_index()
    
    print(f"Reduced to {len(summary_df)} unique food profiles for RAG embedding.")
    
    count = 0
    # To prevent overwhelming the local embedding model, we'll embed the top 2000 most consumed foods.
    # You can remove the slicing [:2000] to embed all, but it will take much longer.
    top_foods = summary_df.sort_values(by='Total_Mean', ascending=False).head(2000)
    
    for index, row in tqdm(top_foods.iterrows(), total=len(top_foods)):
        food_name = row['FoodName']
        countries = row['Country']
        avg_consumption = row['Total_Mean']
        code = row['FoodCode']
        
        content = (
            f"Global Consumption Data for {food_name} (Code: {code}):\n"
            f"This food is primarily consumed in: {countries}.\n"
            f"The average total consumption mean across demographics is {avg_consumption:.2f} grams/day.\n"
            f"This data is sourced from global dietary datasets (CIFOCOSS)."
        )
        
        document_data = {
            "url": f"internal://nutrition/cifocoss/{str(code).lower()}",
            "title": str(food_name),
            "content": content,
            "category": "GLOBAL_CONSUMPTION"
        }
        
        # Load the document into ChromaDB
        intelligence.rag_indexer.index_web_document(document_data)
        count += 1
        
    print(f"\n✓ Successfully embedded {count} unique food consumption profiles into ChromaDB!")

if __name__ == "__main__":
    load_massive_dataset()
