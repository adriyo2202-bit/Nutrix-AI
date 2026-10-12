import sqlite3
import time

t0 = time.time()
conn = sqlite3.connect('nutrix_rag.db')
cursor = conn.cursor()

cursor.execute("SELECT FoodName, Country, Consumers_Mean FROM food_consumption_stats WHERE LOWER(FoodName) LIKE '%meat%' AND LOWER(Country) = 'india' ORDER BY Consumers_Mean DESC LIMIT 20")
rows = cursor.fetchall()
print(f"Rows: {len(rows)}")

if not rows:
    cursor.execute("SELECT FoodName, Country, Consumers_Mean FROM food_consumption_stats WHERE LOWER(FoodName) LIKE '%meat%' ORDER BY Consumers_Mean DESC LIMIT 20")
    rows = cursor.fetchall()
    print(f"Fallback Rows: {len(rows)}")

print(f"Time taken: {time.time()-t0} seconds")
