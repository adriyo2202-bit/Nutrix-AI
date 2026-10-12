import cv2
import numpy as np
import easyocr
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ocr_easyocr_pipeline")

# Initialize EasyOCR reader once
try:
    logger.info("Loading EasyOCR model...")
    reader = easyocr.Reader(['en'], gpu=False) # Use CPU by default to ensure it works on Windows without CUDA issues
except Exception as e:
    logger.error(f"Failed to load EasyOCR: {e}")
    reader = None

def ocr(image_path: str, **kwargs) -> str:
    """
    Runs EasyOCR text extraction on the image.
    """
    if not reader:
        return "OCR Initialization Failed: EasyOCR model not found."

    logger.info(f"Running EasyOCR on {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        return "Error: Image not found or unreadable."
    
    # Read text from image
    try:
        results = reader.readtext(image, detail=0, paragraph=True)
        final_text = "\n".join(results).strip()
        
        if not final_text:
            logger.warning("EasyOCR found no text.")
            return ""
            
        return final_text
    except Exception as e:
        logger.error(f"EasyOCR extraction failed: {e}")
        return ""

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(ocr(sys.argv[1]))
