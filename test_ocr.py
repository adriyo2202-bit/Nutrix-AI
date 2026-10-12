import base64
import requests
import sys

def test_ocr(image_path):
    print(f"Testing OCR on {image_path}")
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode('utf-8')

    url_generate = "http://127.0.0.1:11434/api/generate"
    payload_ocr = {
        "model": "glm-ocr:latest",
        "prompt": "Extract all the text from this image exactly as written.",
        "stream": False,
        "images": [base64_image],
        "options": {
            "num_predict": 2048
        }
    }

    try:
        response = requests.post(url_generate, json=payload_ocr, timeout=120)
        print("Status code:", response.status_code)
        response_json = response.json()
        print("Response keys:", response_json.keys())
        raw_text = response_json.get("response", "").strip()
        print(f"DEBUG GLM-OCR RAW TEXT: {raw_text!r}")
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_ocr(sys.argv[1])
    else:
        test_ocr("test1.png")
