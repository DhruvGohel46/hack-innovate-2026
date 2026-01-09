"""
OCR Engine using EasyOCR for text detection and recognition.
"""
import cv2
import json
from pathlib import Path
import easyocr


def avg_confidence(results):
    """Calculate average confidence from OCR results."""
    if not results:
        return 0.0
    return round(
        sum(x["confidence"] for x in results) / len(results), 3
    )


def filter_main_text(results, min_conf=0.3, min_length=2):
    """Filter meaningful text from OCR results."""
    filtered = []
    for r in results:
        if r["confidence"] >= min_conf and len(r["text"].strip()) >= min_length:
            filtered.append(r)
    return filtered


class OCREngine:
    """EasyOCR-based OCR engine for text detection."""
    
    def __init__(self, languages=["en"], gpu=True):
        """
        Initialize EasyOCR reader.
        
        Args:
            languages: List of language codes (default: ["en"])
            gpu: Use GPU if available (default: True)
        """
        try:
            self.reader = easyocr.Reader(languages, gpu=gpu)
            print(f"[OCR] EasyOCR initialized (GPU={'ON' if gpu else 'OFF'})")
        except Exception as e:
            print(f"[WARNING] GPU initialization failed: {e}")
            if gpu:
                print("[INFO] Falling back to CPU mode...")
                self.reader = easyocr.Reader(languages, gpu=False)
                print("[OCR] EasyOCR initialized (CPU mode)")
            else:
                raise
    
    def run_ocr(self, image_path_or_array):
        """
        Run OCR on an image.
        
        Args:
            image_path_or_array: Path to image (str/Path) or numpy array (cv2 image)
        
        Returns:
            List of dicts with keys: {"text", "confidence"}
        """
        # Handle both file path and numpy array
        if isinstance(image_path_or_array, (str, Path)):
            img = cv2.imread(str(image_path_or_array))
            if img is None:
                print(f"[ERROR] Cannot read image: {image_path_or_array}")
                return []
        else:
            # Assume it's a numpy array (cv2 image)
            img = image_path_or_array
        
        # EasyOCR output: (bbox, text, confidence)
        try:
            results = self.reader.readtext(img)
        except Exception as e:
            print(f"[ERROR] OCR processing failed: {e}")
            return []
        
        ocr_data = []
        for _, text, conf in results:
            ocr_data.append({
                "text": text.strip(),
                "confidence": round(float(conf), 3)
            })
        
        return ocr_data
    
    def compare_images(self, blur_img_path_or_array, enhanced_img_path_or_array, min_conf=0.3, min_length=2):
        """
        Compare OCR results between blur and enhanced images.
        
        Args:
            blur_img_path_or_array: Blur image (path or numpy array)
            enhanced_img_path_or_array: Enhanced image (path or numpy array)
            min_conf: Minimum confidence for filtering (default: 0.3)
            min_length: Minimum text length for filtering (default: 2)
        
        Returns:
            Dict with comparison results
        """
        # Run OCR on both images
        blur_raw = self.run_ocr(blur_img_path_or_array)
        enhanced_raw = self.run_ocr(enhanced_img_path_or_array)
        
        # Calculate averages
        blur_avg_raw = avg_confidence(blur_raw)
        enhanced_avg_raw = avg_confidence(enhanced_raw)
        
        # Filter results
        blur_filtered = filter_main_text(blur_raw, min_conf, min_length)
        enhanced_filtered = filter_main_text(enhanced_raw, min_conf, min_length)
        
        # Build comparison dict
        comparison = {
            "blur": {
                "avg_confidence_raw": blur_avg_raw,
                "text_count_raw": len(blur_raw),
                "texts_raw": blur_raw,
                "text_count_filtered": len(blur_filtered),
                "texts_filtered": blur_filtered
            },
            "enhanced": {
                "avg_confidence_raw": enhanced_avg_raw,
                "text_count_raw": len(enhanced_raw),
                "texts_raw": enhanced_raw,
                "text_count_filtered": len(enhanced_filtered),
                "texts_filtered": enhanced_filtered
            },
            "improvement": {
                "confidence_delta_raw": round(enhanced_avg_raw - blur_avg_raw, 3),
                "text_count_delta_filtered": len(enhanced_filtered) - len(blur_filtered)
            }
        }
        
        return comparison


# Global instance for reuse
_ocr_engine = None


def get_ocr_engine(languages=["en"], gpu=True):
    """Get or create global OCR engine instance."""
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = OCREngine(languages=languages, gpu=gpu)
    return _ocr_engine
