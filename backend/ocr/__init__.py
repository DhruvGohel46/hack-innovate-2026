"""
OCR module for text detection and recognition using EasyOCR.
"""
from .ocr_engine import OCREngine, get_ocr_engine, avg_confidence, filter_main_text

__all__ = ['OCREngine', 'get_ocr_engine', 'avg_confidence', 'filter_main_text']
