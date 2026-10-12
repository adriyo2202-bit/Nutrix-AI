import os
import sys

# Ensure project root is in path to import from project.ocr_new and project.ingre_demo_1
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project.ocr_new import ocr
from project.ingre_demo_1 import NutriScanAnalyzer

def run_label_analysis(image_path: str) -> dict:
    """
    Runs OCR on the given image path, and passes the refined text to the NutriScanAnalyzer (local Ollama LLM).
    Returns the analysis result as a dictionary.
    """
    try:
        # Step 1: Run OCR on the image
        print(f"Running OCR on {image_path}...")
        refined_text = ocr(image_path, use_docling=True, amplify=False)
        print("OCR extracted text:", refined_text[:200].replace('\n', ' '), "...")
        
        # Step 2: Pass text to the Local Analyzer
        print("Analyzing ingredients with Local Model...")
        analyzer = NutriScanAnalyzer()
        result = analyzer.analyze_from_ocr_text(refined_text)
        
        # Return structured dict
        from dataclasses import asdict
        return asdict(result)
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        raise e
