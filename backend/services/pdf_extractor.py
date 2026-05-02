import io
import logging

import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes

from domain.interfaces import PDFExtractorInterface

logger = logging.getLogger(__name__)

# Umbral para decidir si el texto nativo es suficiente. Si pdfplumber devuelve
# menos que esto, asumimos que el PDF es escaneado y caemos a OCR.
MIN_NATIVE_TEXT_LEN = 50

# Idiomas de Tesseract: español + inglés cubre la mayoría de CVs regionales.
OCR_LANGS = "spa+eng"

# DPI para rasterizar el PDF antes de OCR. 200 es buen balance velocidad/calidad.
OCR_DPI = 200


class PDFExtractorService(PDFExtractorInterface):
    def extract_text(self, pdf_bytes: bytes) -> str:
        native = self._extract_native(pdf_bytes)

        if len(native) >= MIN_NATIVE_TEXT_LEN:
            logger.info("PDF con texto nativo (%d chars)", len(native))
            return native

        logger.info("PDF escaneado o sin texto nativo, cayendo a OCR")
        return self._extract_ocr(pdf_bytes)

    def _extract_native(self, pdf_bytes: bytes) -> str:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages).strip()

    def _extract_ocr(self, pdf_bytes: bytes) -> str:
        images = convert_from_bytes(pdf_bytes, dpi=OCR_DPI)
        pages = [pytesseract.image_to_string(img, lang=OCR_LANGS) for img in images]
        return "\n".join(pages).strip()
