"""
Resume parser module for text extraction and section segmentation.
"""

from .extractor import (
    extract_text,
    extract_contact_info,
    clean_text,
    extract_text_from_pdf,
    extract_text_from_docx,
)
from .section_detector import detect_sections, compute_section_hygiene

__all__ = [
    "extract_text",
    "extract_contact_info",
    "clean_text",
    "extract_text_from_pdf",
    "extract_text_from_docx",
    "detect_sections",
    "compute_section_hygiene",
]
