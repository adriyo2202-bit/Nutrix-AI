from datetime import datetime
from typing import List, Tuple, Dict
import numpy as np
import pandas as pd
import sqlite3
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from diet_planner.db import get_daily_logged_nutrition

def get_meal_context() -> str:
    """Detects the time of day and returns the corresponding meal context."""
    hour = datetime.now().hour
    if 6 <= hour < 10:
        return "breakfast"
    elif 10 <= hour < 13:
        return "mid-morning snack"
    elif 13 <= hour < 16:
        return "lunch"
    elif 16 <= hour < 19:
        return "evening snack"
    else:
        return "dinner"


def get_remaining_macros(
    user_id: str,
    daily_cal: float,
    daily_prot: float,
    daily_carb: float
) -> Tuple[float, float, float]:
    """Retrieves today's logged meals and computes remaining nutritional budget."""
    today = datetime.today().date().isoformat()
    logged = get_daily_logged_nutrition(user_id, today)
    
    # Enforce minimums of remaining nutrients to avoid math issues with zeros or negatives
    rem_cal = max(daily_cal - logged["calories"], 100.0)
    rem_prot = max(daily_prot - logged["protein"], 5.0)
    rem_carb = max(daily_carb - logged["carbs"], 10.0)
    
    return rem_cal, rem_prot, rem_carb


def generate_reason(food: pd.Series, user_goal: str, remaining_protein: float, remaining_calories: float) -> str:
    """Generates a one-line explanation of why a food item is a good fit."""
    goal_clean = user_goal.lower()
    if goal_clean == "weight_loss":
        return "Low calorie, high fibre — keeps you full without overshooting your budget"
    elif goal_clean == "weight_gain" and food["protein_g"] > 10:
        return f"High protein ({food['protein_g']}g) — helps meet your {remaining_protein:.1f}g remaining protein target"
    else:
        return f"Fits your remaining calorie budget of {remaining_calories:.1f} kcal"


def recommend_foods(
    user_id: str,
    daily_cal: float,
    daily_prot: float,
    daily_carb: float,
    user_allergens: List[str],
    user_goal: str,
    meal_context: str,
    n: int = 5
) -> pd.DataFrame:
    """
    Content-Based Food Recommender:
    Matches user's current remaining macro need vector [cal, prot, carb] 
    against IFCT food vectors using cosine similarity.
    Applies hard filters for allergens and calorie budgets.
    """
    # 1. Get remaining needs
    rem_cal, rem_prot, rem_carb = get_remaining_macros(user_id, daily_cal, daily_prot, daily_carb)
    
    # 2. Load food database
    conn = sqlite3.connect("ifct.db")
    foods_df = pd.read_sql("SELECT name, calories, protein_g, carbs_g, fat_g, allergens FROM foods", conn)
    conn.close()
    
    if foods_df.empty:
        return pd.DataFrame()

    # 3. Hard filter: remove allergen items
    for allergen in user_allergens:
        allergen = allergen.strip().lower()
        if allergen:
            # Drop rows where the allergens column contains the user allergen string
            foods_df = foods_df[~foods_df["allergens"].str.contains(allergen, case=False, na=False)]
            
    if foods_df.empty:
        return pd.DataFrame()

    # 4. Filter by calorie range: within 130% of per-meal budget
    # per-meal budget is remaining budget divided by 2 to prevent eating it all in one meal
    per_meal_budget = rem_cal / 2.0
    filtered_df = foods_df[foods_df["calories"] <= per_meal_budget * 1.3].copy()
    
    # Fallback: if budget filtering yields empty list, relax the constraint to total remaining calories
    if filtered_df.empty:
        filtered_df = foods_df[foods_df["calories"] <= rem_cal].copy()
        
    if filtered_df.empty:
        # If still empty (e.g. remaining calories very low), use the lowest calorie food items
        filtered_df = foods_df.nsmallest(5, "calories").copy()

    # 5. Extract vector matrices and compute cosine similarity
    user_vector = np.array([[rem_cal, rem_prot, rem_carb]])
    food_matrix = filtered_df[["calories", "protein_g", "carbs_g"]].values
    
    # Normalize vectors to unit length
    user_norm = normalize(user_vector)
    food_norm = normalize(food_matrix)
    
    # Compute scores
    scores = cosine_similarity(user_norm, food_norm)[0]
    filtered_df["score"] = scores
    
    # 6. Take top n and generate reasons
    top_df = filtered_df.nlargest(n, "score").copy()
    
    reasons = []
    for _, row in top_df.iterrows():
        reason = generate_reason(row, user_goal, rem_prot, rem_cal)
        reasons.append(reason)
    top_df["why_it_fits"] = reasons
    
    return top_df[["name", "calories", "protein_g", "carbs_g", "fat_g", "why_it_fits"]]
