import os
import sys
import json
import sqlite3
import urllib.request
import urllib.error

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



import base64

def get_ingredient_safety_rules(raw_text: str) -> str:
    """Queries the SQLite RAG DB for rules related to words found in the OCR text."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'nutrix_rag.db')
    if not os.path.exists(db_path):
        return "RAG database not found."
        
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Simple keyword extraction (words longer than 4 chars)
        words = [w.strip(".,;:()") for w in raw_text.split() if len(w) > 4]
        if not words:
            return "No valid keywords for RAG."
            
        rules = []
        for word in set(words[:20]): # Limit to first 20 unique words to avoid massive queries
            cursor.execute("SELECT ingredient_name, fssai_status, eu_status, primary_health_risks FROM ingredient_safety_rules WHERE LOWER(ingredient_name) LIKE ?", (f"%{word.lower()}%",))
            for row in cursor.fetchall():
                rules.append(f"- {row['ingredient_name']}: EU Status: {row['eu_status']}, FSSAI: {row['fssai_status']}. Risks: {row['primary_health_risks']}")
                
        conn.close()
        # Deduplicate and return
        unique_rules = list(set(rules))
        if not unique_rules:
             return "No matching RAG safety rules found in database."
        return "\n".join(unique_rules[:15]) # Limit to 15 rules max for context
    except Exception as e:
        return f"RAG error: {e}"

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def run_label_analysis(image_path: str) -> dict:
    """
    Passes the image directly to the Ollama glm-ocr Model to extract text,
    then fetches RAG rules, and passes the text and rules to Qwen 3.5 for analysis.
    """
    print(f"Running LLM Vision Analysis on {image_path}...")
    try:
        base64_image = encode_image_to_base64(image_path)
    except Exception as e:
        return {"error": f"Failed to read image file: {e}"}

    # Step 1: Extract Text using glm-ocr
    url_generate = "http://127.0.0.1:11434/api/generate"
    payload_ocr = {
        "model": "glm-ocr:latest",
        "prompt": "Extract all the text from this image exactly as written.",
        "stream": True,
        "images": [base64_image],
        "options": {
            "num_predict": 2048,
            "num_ctx": 8192
        }
    }
    print(f"Calling Ollama/LLM Server (glm-ocr:latest) at {url_generate} for OCR Extraction...")
    import requests
    try:
        response = requests.post(url_generate, json=payload_ocr, stream=True, timeout=600)
        raw_text = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    if "error" in data:
                        print(f"Ollama stream error: {data['error']}")
                        break
                    raw_text += data.get("response", "")
                    if data.get("done"):
                        break
                except Exception as ex:
                    print(f"Error parsing JSON line: {ex}")
        print(f"DEBUG GLM-OCR RAW TEXT: {raw_text!r}")
        
        # GLM-OCR can hallucinate by repeating the same text infinitely. Clean it up.
        lines = raw_text.split('\n')
        seen = set()
        clean_lines = []
        for line in lines:
            ls = line.strip()
            if ls and ls not in seen and not ls.startswith('```'):
                seen.add(ls)
                clean_lines.append(ls)
        extracted_text = "\n".join(clean_lines)[:4000] # Cap at 4000 chars
        print(f"GLM-OCR Extracted text length (cleaned): {len(extracted_text)}")
    except Exception as e:
        return {"error": f"GLM-OCR Extraction failed: {e}"}
        
    if not extracted_text:
        return {"error": "OCR did not extract any text from the image. Please try a clearer image."}

    # Step 2: Get RAG Safety Rules
    rag_context = get_ingredient_safety_rules(extracted_text)

    # Step 3: Analyze with Qwen 3.5
    prompt = f"""You are 'Healthy Food AI', an expert nutrition and food safety analyst. 
I have extracted the following text from a food nutrition/ingredient label using OCR:
---
{extracted_text}
---

Here are some known safety rules for some of these ingredients from our database:
---
{rag_context}
---

Based on the extracted text and the safety rules, analyze the ingredients AND nutritional facts (like sodium, sugar, fats) for health, safety, and EU standards. Also suggest healthy alternatives.

IMPORTANT: If the text contains nutritional facts (e.g., Sodium, Added Sugar, Fat) but no specific ingredients, evaluate the safety score based on those nutritional values. List the concerning or beneficial nutrients in the "ingredients" array (e.g., {{"name": "Sodium (1028mg)", "safety_verdict": "unsafe", "safety_reason": "High sodium content can lead to hypertension."}}).

IMPORTANT: If the extracted text does NOT contain ANY food ingredients AND does NOT contain ANY nutritional facts, you MUST set "overall_safety_score" to 0, "summary_bn_en" to "Healthy Food AI cannot detect any ingredients or nutritional information in this text.", and leave "ingredients" empty.

IMPORTANT: You MUST respond with a JSON object exactly matching this simplified structure. Do NOT include markdown tags, just the raw JSON. The summary MUST be in English.

{{
  "overall_safety_score": <integer from 0 to 100>,
  "summary_bn_en": "A single string containing a summary of the product's safety based on ingredients or nutritional facts. Include a section for 'Healthy Alternatives'.",
  "ingredients": [
    {{
      "name": "Ingredient or Nutrient Name",
      "safety_verdict": "safe" | "caution" | "unsafe",
      "safety_reason": "Short explanation of why it is safe/unsafe."
    }}
  ]
}}
"""

    url_chat = "http://127.0.0.1:11434/api/chat" # Hardcoded to native API for num_ctx support
    model = os.environ.get("OLLAMA_MODEL", "qwen3.5:9b")
    headers = {
        "Content-Type": "application/json"
    }
    
    if "v1/chat/completions" in url_chat:
        payload_chat = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "stream": False
        }
    else:
        payload_chat = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "stream": False,
            "options": {
                "num_predict": 4096,
                "num_ctx": 8192
            }
        }
    
    print(f"Calling Ollama/LLM Server ({model}) at {url_chat} for Analysis...")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url_chat, json=payload_chat, headers=headers, timeout=600)
            response_json = response.json()
            if "choices" in response_json:
                result_text = response_json["choices"][0]["message"]["content"].strip()
            else:
                result_text = response_json["message"]["content"].strip()
                
            if not result_text:
                print(f"Attempt {attempt+1}: Ollama returned an empty string.")
                if attempt < max_retries - 1:
                    continue
                raise ValueError("Ollama returned an empty string after multiple attempts.")

            # Robustly extract JSON object using regex, ignoring <think> blocks and markdown
            import re
            match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if match:
                result_text = match.group(0)
            else:
                print(f"Attempt {attempt+1}: No valid JSON object found in the response.")
                if attempt < max_retries - 1:
                    continue
                raise ValueError("No valid JSON object found in the response.")

            parsed_json = json.loads(result_text)

            # Enforce string types for UI compatibility
            if isinstance(parsed_json.get("product_ingredients_raw"), dict):
                parsed_json["product_ingredients_raw"] = json.dumps(parsed_json["product_ingredients_raw"], indent=2)
            if isinstance(parsed_json.get("summary_bn_en"), dict):
                summary = parsed_json["summary_bn_en"]
                if "en" in summary and "bn" in summary:
                    parsed_json["summary_bn_en"] = f"{json.dumps(summary['en'], indent=2)}\n\n{json.dumps(summary['bn'], indent=2)}"
                else:
                    parsed_json["summary_bn_en"] = json.dumps(summary, indent=2)
                    
            print("Unified Analysis Complete with Real Ollama AI!")
            return parsed_json
            
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt == max_retries - 1:
                print(f"Error calling LLM API: {e}. Returning error dictionary.")
                return {"error": f"AI Analysis failed: {e}. Please ensure Ollama is running and returning valid JSON."}



