import sqlite3
import pandas as pd
import os
from pathlib import Path

def ingest():
    project_root = Path(__file__).resolve().parent.parent.parent
    db_path = project_root / 'Source_Code' / 'nutrix_rag.db'
    dataset_dir = project_root / 'dataset'

    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    
    # 1. Ingest fullcifocoss.csv
    cifocoss_path = dataset_dir / 'fullcifocoss.csv'
    if cifocoss_path.exists():
        print(f"Ingesting {cifocoss_path} (this may take a minute for 131MB)...")
        # The file appears to use semicolons based on earlier head command
        df_cifocoss = pd.read_csv(cifocoss_path, sep=';', low_memory=False)
        # Write to SQLite
        df_cifocoss.to_sql('food_consumption_stats', conn, if_exists='replace', index=False)
        print("Successfully loaded food_consumption_stats table.")
    else:
        print(f"File not found: {cifocoss_path}")

    # 2. Ingest ingredient_safety_rules.csv
    safety_path = dataset_dir / 'ingredient_safety_rules.csv'
    if safety_path.exists():
        print(f"Ingesting {safety_path}...")
        df_safety = pd.read_csv(safety_path)
        df_safety.to_sql('ingredient_safety_rules', conn, if_exists='replace', index=False)
        print("Successfully loaded ingredient_safety_rules table.")
    else:
        print(f"File not found: {safety_path}")

    conn.close()
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest()
