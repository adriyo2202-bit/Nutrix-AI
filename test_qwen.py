import requests

def test_qwen():
    prompt = """You are 'Healthy Food AI', an expert nutrition and food safety analyst. 
I have extracted the following text from a food nutrition/ingredient label using OCR:
---
Nutritional Information

If a serve is 70 g

Nutrition Information*

Per 100g

Per Serve

%GDA# Per Serve

Energy (kcal) 384 269 13%
Protein (g) 8.2 5.7 11%
Carbohydrate (g) 59.6 41.7 16%
-Total Sugars (g) 1.8 1.3 1%
-Added Sugars (g) 1.3 0.9 -
Total Fat (g) 12.5 8.8 13%
-Saturated Fat (g) (not more than) 8.2 5.7 29%
-Trans Fat (g) (not more than) 0.13 0.09 -
Sodium (mg) 1028.3 719.8 30%
%RDA^ Per Serve
^Iron (mg) 6.90 4.83 16%

#Guideline Daily Amounts of an average adult (2000 kcal). Pack contains 1 serve.
Per serve contribution to RDA - 13% energy, 2% added sugar, 13% total fat, 26% saturated fat, 5% trans fat and 36% sodium.
~One serve (70 g) of MAGGI Masala Noodles meets 16% Iron RDA for sedentary adults and 15% Iron RDA for 16-17 year old teenagers (ICMR, 2020)

Maggi
2-Minute noodles
Masala*

Creative Visualization. Suggested Garnishing.
Enjoy your MAGGI noodles (steamed, dried and fried) and consume a variety of other foods like vegetables, fruits and milk.
*Approximate Value
---

Here are some known safety rules for some of these ingredients from our database:
---

---

Based on the extracted text and the safety rules, analyze the ingredients for health, safety, and EU standards. Also suggest healthy alternatives.

IMPORTANT: If the extracted text does NOT contain any valid food ingredients, you MUST set "overall_safety_score" to 0, "summary_bn_en" to "Healthy Food AI cannot detect any ingredients in this text.", and leave "ingredients" empty.

IMPORTANT: You MUST respond with a JSON object exactly matching this simplified structure. Do NOT include markdown tags, just the raw JSON. The summary MUST be in English.

{
  "overall_safety_score": <integer from 0 to 100>,
  "summary_bn_en": "A single string containing a summary of the product's safety. Include a section for 'Healthy Alternatives'.",
  "ingredients": [
    {
      "name": "Ingredient Name",
      "safety_verdict": "safe" | "caution" | "unsafe",
      "safety_reason": "Short explanation of why it is safe/unsafe, mentioning EU rules if applicable."
    }
  ]
}
"""
    payload_chat = {
        "model": "qwen3.5:9b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "stream": False,
        "options": {
            "num_predict": 4096,
            "num_ctx": 8192
        }
    }
    try:
        response = requests.post("http://127.0.0.1:11434/api/chat", json=payload_chat, timeout=120)
        print("Status code:", response.status_code)
        response_json = response.json()
        print(response_json)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_qwen()
