import sqlite3
import pandas as pd

def seed():
    # Define a list of classic Indian food items based on IFCT average guidelines.
    # We include standard calories, protein, carbs, fats, and any allergen tags.
    data = [
        # Grains and Breads
        {"name": "Whole Wheat Roti", "calories": 85.0, "protein_g": 3.0, "carbs_g": 18.0, "fat_g": 0.5, "allergens": "gluten"},
        {"name": "Phulka", "calories": 70.0, "protein_g": 2.5, "carbs_g": 15.0, "fat_g": 0.2, "allergens": "gluten"},
        {"name": "Brown Rice (1 cup cooked)", "calories": 215.0, "protein_g": 5.0, "carbs_g": 45.0, "fat_g": 1.6, "allergens": ""},
        {"name": "White Rice (1 cup cooked)", "calories": 205.0, "protein_g": 4.2, "carbs_g": 44.5, "fat_g": 0.4, "allergens": ""},
        {"name": "Maida Lacha Paratha", "calories": 290.0, "protein_g": 6.0, "carbs_g": 48.0, "fat_g": 8.5, "allergens": "gluten"},
        {"name": "Quinoa (1 cup cooked)", "calories": 222.0, "protein_g": 8.0, "carbs_g": 39.0, "fat_g": 3.6, "allergens": ""},
        {"name": "Oats (1 cup cooked)", "calories": 166.0, "protein_g": 6.0, "carbs_g": 28.0, "fat_g": 4.0, "allergens": ""},
        {"name": "Barley (1 cup cooked)", "calories": 193.0, "protein_g": 3.6, "carbs_g": 44.0, "fat_g": 0.7, "allergens": "gluten"},

        # Protein Dishes (Dairy/Veg)
        {"name": "Paneer Tikka (100g)", "calories": 240.0, "protein_g": 18.0, "carbs_g": 5.0, "fat_g": 16.0, "allergens": "lactose"},
        {"name": "Palak Paneer (1 bowl)", "calories": 220.0, "protein_g": 12.0, "carbs_g": 8.0, "fat_g": 15.0, "allergens": "lactose"},
        {"name": "Curd (1 cup, 150g)", "calories": 100.0, "protein_g": 5.0, "carbs_g": 7.0, "fat_g": 6.0, "allergens": "lactose"},
        {"name": "Tofu Stir-fry (100g tofu)", "calories": 180.0, "protein_g": 12.0, "carbs_g": 6.0, "fat_g": 11.0, "allergens": "soy"},
        {"name": "Soya Chunks Curry (1 bowl)", "calories": 210.0, "protein_g": 22.0, "carbs_g": 16.0, "fat_g": 5.0, "allergens": "soy"},

        # Legumes and Dals
        {"name": "Dal Tadka (1 bowl)", "calories": 150.0, "protein_g": 8.0, "carbs_g": 22.0, "fat_g": 4.0, "allergens": ""},
        {"name": "Moong Dal (1 bowl)", "calories": 140.0, "protein_g": 9.0, "carbs_g": 21.0, "fat_g": 3.0, "allergens": ""},
        {"name": "Dal Makhani (1 bowl)", "calories": 280.0, "protein_g": 10.0, "carbs_g": 32.0, "fat_g": 12.0, "allergens": "lactose"},
        {"name": "Rajma Masala (1 bowl)", "calories": 180.0, "protein_g": 9.5, "carbs_g": 28.0, "fat_g": 4.0, "allergens": ""},
        {"name": "Chana Masala (1 bowl)", "calories": 200.0, "protein_g": 10.0, "carbs_g": 30.0, "fat_g": 4.5, "allergens": ""},
        {"name": "Moong Dal Cheela", "calories": 180.0, "protein_g": 9.0, "carbs_g": 26.0, "fat_g": 4.0, "allergens": ""},
        {"name": "Sprouts Salad (1 bowl)", "calories": 150.0, "protein_g": 8.0, "carbs_g": 24.0, "fat_g": 1.0, "allergens": ""},

        # Egg and Non-Veg
        {"name": "Boiled Eggs (2 pieces)", "calories": 155.0, "protein_g": 13.0, "carbs_g": 1.1, "fat_g": 11.0, "allergens": "egg"},
        {"name": "Egg Omelette (2 eggs)", "calories": 180.0, "protein_g": 14.0, "carbs_g": 2.0, "fat_g": 13.0, "allergens": "egg"},
        {"name": "Egg Bhurji (2 eggs)", "calories": 210.0, "protein_g": 14.0, "carbs_g": 4.0, "fat_g": 15.0, "allergens": "egg"},
        {"name": "Chicken Curry (150g)", "calories": 260.0, "protein_g": 26.0, "carbs_g": 6.0, "fat_g": 14.0, "allergens": ""},
        {"name": "Chicken Tikka (150g)", "calories": 220.0, "protein_g": 30.0, "carbs_g": 4.0, "fat_g": 8.5, "allergens": ""},
        {"name": "Fish Curry (120g)", "calories": 180.0, "protein_g": 22.0, "carbs_g": 5.0, "fat_g": 8.0, "allergens": "fish"},
        {"name": "Grilled Fish Fillet", "calories": 160.0, "protein_g": 24.0, "carbs_g": 1.0, "fat_g": 6.5, "allergens": "fish"},

        # Vegetables
        {"name": "Bhindi Sabji (1 bowl)", "calories": 110.0, "protein_g": 2.0, "carbs_g": 12.0, "fat_g": 6.0, "allergens": ""},
        {"name": "Lauki Sabji (1 bowl)", "calories": 80.0, "protein_g": 1.5, "carbs_g": 9.0, "fat_g": 4.0, "allergens": ""},
        {"name": "Bhindi Fry", "calories": 150.0, "protein_g": 2.2, "carbs_g": 14.0, "fat_g": 10.0, "allergens": ""},
        {"name": "Methi Matar Malai", "calories": 240.0, "protein_g": 6.0, "carbs_g": 18.0, "fat_g": 16.0, "allergens": "lactose"},
        {"name": "Sweet Potato (100g)", "calories": 86.0, "protein_g": 1.6, "carbs_g": 20.0, "fat_g": 0.1, "allergens": ""},

        # Breakfast & Snacks
        {"name": "Vegetable Poha", "calories": 220.0, "protein_g": 4.0, "carbs_g": 38.0, "fat_g": 5.0, "allergens": ""},
        {"name": "Oats Upma", "calories": 210.0, "protein_g": 6.0, "carbs_g": 35.0, "fat_g": 4.0, "allergens": ""},
        {"name": "Idli (2 pieces)", "calories": 160.0, "protein_g": 4.0, "carbs_g": 35.0, "fat_g": 0.5, "allergens": ""},
        {"name": "Sambar (1 bowl)", "calories": 70.0, "protein_g": 2.0, "carbs_g": 9.0, "fat_g": 3.0, "allergens": ""},
        {"name": "Upma", "calories": 200.0, "protein_g": 4.5, "carbs_g": 36.0, "fat_g": 4.0, "allergens": ""},
        {"name": "Roasted Makhana (25g)", "calories": 90.0, "protein_g": 2.5, "carbs_g": 18.0, "fat_g": 0.5, "allergens": ""},
        {"name": "Roasted Chana (40g)", "calories": 140.0, "protein_g": 7.0, "carbs_g": 22.0, "fat_g": 2.0, "allergens": ""},
        {"name": "Mixed Nuts (15g)", "calories": 95.0, "protein_g": 3.0, "carbs_g": 3.0, "fat_g": 8.0, "allergens": "nuts"},
        {"name": "Almonds (10g)", "calories": 60.0, "protein_g": 2.0, "carbs_g": 2.0, "fat_g": 5.0, "allergens": "nuts"},
        {"name": "Walnuts (10g)", "calories": 65.0, "protein_g": 1.5, "carbs_g": 1.4, "fat_g": 6.5, "allergens": "nuts"},
        {"name": "Masala Chaas (Buttermilk)", "calories": 45.0, "protein_g": 2.0, "carbs_g": 3.0, "fat_g": 1.5, "allergens": "lactose"},
        
        # Excludes / Health filter demo items
        {"name": "Mango Pickle", "calories": 40.0, "protein_g": 0.5, "carbs_g": 4.0, "fat_g": 2.5, "allergens": ""},
        {"name": "Papad (1 piece)", "calories": 45.0, "protein_g": 2.0, "carbs_g": 8.0, "fat_g": 0.5, "allergens": ""},
        {"name": "Processed Cheese", "calories": 320.0, "protein_g": 18.0, "carbs_g": 1.5, "fat_g": 26.0, "allergens": "lactose"}
    ]
    
    # Write to CSV
    csv_file = "ifct_data.csv"
    df = pd.DataFrame(data)
    df.to_csv(csv_file, index=False)
    print(f"✓ programmatically created {csv_file}")
    
    # Load into SQLite
    conn = sqlite3.connect("ifct.db")
    df_loaded = pd.read_csv(csv_file)
    df_loaded.to_sql("foods", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    print("✓ Successfully loaded CSV data into ifct.db inside table 'foods'")

if __name__ == "__main__":
    seed()
