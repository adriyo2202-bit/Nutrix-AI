import sqlite3
import os
from typing import Tuple, Optional, List, Dict

DB_NUTRISCAN = "nutriscan.db"
DB_IFCT = "ifct.db"

def init_databases():
    """Initializes nutriscan.db schemas."""
    conn = sqlite3.connect(DB_NUTRISCAN)
    cursor = conn.cursor()
    
    # User Profiles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            age INTEGER,
            height REAL,
            weight REAL,
            gender TEXT,
            activity_level TEXT,
            food_preference TEXT,
            goal TEXT,
            health_conditions TEXT,
            allergens TEXT
        )
    """)
    
    # Weight Logs for Recalibration
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weight_log (
            user_id TEXT,
            date TEXT,
            weight REAL
        )
    """)
    
    # Meal Log for suggestions budget
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meal_log (
            user_id TEXT,
            date TEXT,
            meal_type TEXT,
            food_name TEXT,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL
        )
    """)
    
    conn.commit()
    conn.close()


def save_user_profile(profile_dict: dict):
    init_databases()
    conn = sqlite3.connect(DB_NUTRISCAN)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO user_profiles 
        (user_id, age, height, weight, gender, activity_level, food_preference, goal, health_conditions, allergens)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        profile_dict['user_id'],
        profile_dict['age'],
        profile_dict['height'],
        profile_dict['weight'],
        profile_dict['gender'],
        profile_dict['activity_level'],
        profile_dict['food_preference'],
        profile_dict['goal'],
        ",".join(profile_dict['health_conditions']),
        ",".join(profile_dict['allergens'])
    ))
    conn.commit()
    conn.close()


def get_user_profile(user_id: str) -> Optional[dict]:
    init_databases()
    conn = sqlite3.connect(DB_NUTRISCAN)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'user_id': row['user_id'],
            'age': row['age'],
            'height': row['height'],
            'weight': row['weight'],
            'gender': row['gender'],
            'activity_level': row['activity_level'],
            'food_preference': row['food_preference'],
            'goal': row['goal'],
            'health_conditions': [c.strip() for c in row['health_conditions'].split(",") if c.strip()],
            'allergens': [a.strip() for a in row['allergens'].split(",") if a.strip()]
        }
    return None


def log_weight(user_id: str, weight: float, date_str: str):
    init_databases()
    conn = sqlite3.connect(DB_NUTRISCAN)
    cursor = conn.cursor()
    # Check if entry for date already exists to overwrite, otherwise insert
    cursor.execute("SELECT 1 FROM weight_log WHERE user_id=? AND date=?", (user_id, date_str))
    if cursor.fetchone():
        cursor.execute("UPDATE weight_log SET weight=? WHERE user_id=? AND date=?", (weight, user_id, date_str))
    else:
        cursor.execute("INSERT INTO weight_log (user_id, date, weight) VALUES (?, ?, ?)", (user_id, date_str, weight))
    conn.commit()
    conn.close()


def get_weight_logs(user_id: str) -> List[Tuple[str, float]]:
    init_databases()
    conn = sqlite3.connect(DB_NUTRISCAN)
    cursor = conn.cursor()
    cursor.execute("SELECT date, weight FROM weight_log WHERE user_id = ? ORDER BY date ASC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def log_meal(user_id: str, date_str: str, meal_type: str, food_name: str, cal: float, prot: float, carb: float, fat: float):
    init_databases()
    conn = sqlite3.connect(DB_NUTRISCAN)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meal_log (user_id, date, meal_type, food_name, calories, protein, carbs, fat)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, date_str, meal_type, food_name, cal, prot, carb, fat))
    conn.commit()
    conn.close()


def get_daily_logged_nutrition(user_id: str, date_str: str) -> Dict[str, float]:
    init_databases()
    conn = sqlite3.connect(DB_NUTRISCAN)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(calories), SUM(protein), SUM(carbs), SUM(fat) 
        FROM meal_log 
        WHERE user_id = ? AND date = ?
    """, (user_id, date_str))
    row = cursor.fetchone()
    conn.close()
    
    cal = row[0] or 0.0
    prot = row[1] or 0.0
    carb = row[2] or 0.0
    fat = row[3] or 0.0
    
    return {"calories": cal, "protein": prot, "carbs": carb, "fat": fat}


def get_nutrition_from_ifct(meal_name: str) -> Optional[Tuple[str, float, float, float, float]]:
    """
    Looks up a food item in the IFCT database.
    Returns: (name, calories, protein_g, carbs_g, fat_g)
    """
    if not os.path.exists(DB_IFCT):
        return None
    conn = sqlite3.connect(DB_IFCT)
    cursor = conn.cursor()
    # Try exact match or sub-phrase match
    cursor.execute(
        "SELECT name, calories, protein_g, carbs_g, fat_g FROM foods WHERE name LIKE ? LIMIT 1",
        (f"%{meal_name}%",)
    )
    res = cursor.fetchone()
    conn.close()
    return res
