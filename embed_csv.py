import sqlite3
import csv
import sys
import os

db_path = 'nutrix_rag.db'
csv_path = 'fullcifocoss.csv'

if not os.path.exists(csv_path):
    print(f"File {csv_path} not found.")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS food_consumption_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    FoodName TEXT,
    Country TEXT,
    Consumers_Mean REAL
)
""")

# Clear existing data just in case
cursor.execute("DELETE FROM food_consumption_stats")

print("Reading CSV and inserting data (this may take a minute)...")

count = 0
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    
    batch = []
    for row in reader:
        try:
            food_name = row['FoodName']
            country = row['Country']
            mean_str = row['Consumers_Mean']
            
            # Skip if mean is empty
            if not mean_str:
                mean_val = 0.0
            else:
                mean_val = float(mean_str.replace(',', '.'))
                
            batch.append((food_name, country, mean_val))
            count += 1
            
            if len(batch) >= 10000:
                cursor.executemany("INSERT INTO food_consumption_stats (FoodName, Country, Consumers_Mean) VALUES (?, ?, ?)", batch)
                batch = []
                
        except Exception as e:
            continue
            
    if batch:
        cursor.executemany("INSERT INTO food_consumption_stats (FoodName, Country, Consumers_Mean) VALUES (?, ?, ?)", batch)

conn.commit()
conn.close()

print(f"Successfully embedded {count} rows into food_consumption_stats table in nutrix_rag.db")
