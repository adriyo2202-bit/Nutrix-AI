import json
import urllib.request
import urllib.error
import sqlite3
import os
import random

def get_popular_foods(diet_type: str, limit: int = 5) -> str:
    """Queries the RAG database for popular/consumed foods matching the diet type, specifically focusing on India."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'nutrix_rag.db')
    if not os.path.exists(db_path):
        return "Local dataset unavailable."
        
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # We look up food_consumption_stats based on keywords matching the diet, strictly for India
        search_kw = "%"
        if "veg" in diet_type.lower() and "non" not in diet_type.lower():
            search_kw = "%vegetable%"
        elif "protein" in diet_type.lower():
            search_kw = "%meat%"
            
        # Target foods consumed in India
        cursor.execute("SELECT FoodName, Country, Consumers_Mean FROM food_consumption_stats WHERE LOWER(FoodName) LIKE ? AND LOWER(Country) = 'india' ORDER BY Consumers_Mean DESC LIMIT 20", (search_kw,))
        rows = cursor.fetchall()
        
        # Fallback to general foods if India-specific data is sparse
        if not rows:
             cursor.execute("SELECT FoodName, Country, Consumers_Mean FROM food_consumption_stats WHERE LOWER(FoodName) LIKE ? ORDER BY Consumers_Mean DESC LIMIT 20", (search_kw,))
             rows = cursor.fetchall()
             
        conn.close()
        
        if not rows:
            return "No specific dataset foods found for this diet."
            
        # Pick a random sample from the top 20 to keep diets varied
        sampled = random.sample(rows, min(limit, len(rows)))
        foods = [f"{r['FoodName']} (Popular in {r['Country']}, Consumed by ~{r['Consumers_Mean']}%)" for r in sampled]
        return "\n".join(foods)
    except Exception as e:
        return f"Database error: {e}"

def generate_diet_plan(age: int, height: float, weight: float, goal: str, diet_type: str) -> dict:
    """
    Calls the local Ollama LLM Server to generate an engaging diet plan, 
    incorporating real food consumption data from the SQLite RAG database.
    """
    # 1. Fetch RAG Context
    popular_foods_context = get_popular_foods(diet_type)
        
    prompt = f"""
You are a highly direct, bold, and precise fitness coach.
I am {age} years old, my height is {height} cm, and my weight is {weight} kg.
My fitness goal is: {goal}.
My diet preference is: {diet_type}.

[RAG DATASET - POPULAR FOODS MATCHING DIET]
{popular_foods_context}

INSTRUCTIONS:
1. You MUST design the diet plan according to TRADITIONAL INDIAN STYLE cuisine. Use common Indian meals (e.g., Dal, Roti, Sabzi, Paneer, Chicken Tikka depending on veg/non-veg).
2. You MUST strictly FORBID and REMOVE any mention of beer, alcohol, or western junk food. 
3. You must heavily prioritize using the foods listed in the [RAG DATASET] above in the "mandatory_fuel" and "daily_roadmap" sections.
4. Keep the text values short, highly scannable, and extremely punchy. Do not include extra fluff.

You must return your response as a valid JSON object following this EXACT schema:
{{
  "bmi_verdict": "string (Briefly state BMI and give a STRONG verdict)",
  "goal_alignment": "string (Based on the goal, give a one-sentence direct mandate)",
  "daily_roadmap": {{
    "breakfast": "string",
    "lunch": "string",
    "dinner": "string",
    "snack": "string"
  }},
  "mandatory_fuel": ["list of 3-4 strings (must include dataset foods)"],
  "strictly_forbidden": ["list of 3-4 strings (foods to AVOID completely)"]
}}
"""

    url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1/chat/completions")
    model = os.environ.get("OLLAMA_MODEL", "qwen3.5:9b")
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.4,
        "stream": False,
        "options": {
            "num_predict": 4096
        }
    }

    try:
        import requests
        response = requests.post(url, json=data, headers=headers, timeout=600)
        response.raise_for_status()
        
        result = response.json()
        if "choices" in result:
            text = result["choices"][0]["message"]["content"].strip()
        else:
            text = result["message"]["content"].strip()
            
        if not text:
            raise ValueError("Ollama returned an empty string.")
            
        # Strip thinking tags if present
        if "</think>" in text:
            text = text.split("</think>", 1)[1].strip()

        # Strip markdown code fences if wrapped
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(text[start:end+1])
            raise
    except requests.exceptions.RequestException as e:
        return {"error": f"Ollama/LLM Server unreachable at {url}. Make sure Ollama is running. Error: {e}"}
    except json.JSONDecodeError:
        return {"error": "LLM did not return valid JSON. Please try again."}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}
