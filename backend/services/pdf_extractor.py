import pdfplumber

from domain.interfaces import PDFExtractorInterface


class PDFExtractorService(PDFExtractorInterface):
    def extract_text(self, pdf_bytes: bytes) -> str:
        import io
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages).strip()
