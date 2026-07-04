from io import BytesIO
from pathlib import Path
import fitz  # PyMuPDF
import docx

class ResumeExtractor:
    """
    Responsible for extracting raw text from resume files.
    Supported formats: PDF, DOCX, TXT.
    """
    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

    @staticmethod
    def extract(file_bytes: bytes, filename: str) -> str:
        extension = Path(filename).suffix.lower()

        if extension not in ResumeExtractor.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")

        if extension == ".pdf":
            return ResumeExtractor._extract_pdf(file_bytes)

        if extension == ".docx":
            return ResumeExtractor._extract_docx(file_bytes)

        return file_bytes.decode("utf-8", errors="ignore")

    @staticmethod
    def _extract_pdf(file_bytes: bytes) -> str:
        text = ""
        document = fitz.open(stream=file_bytes, filetype="pdf")

        for page in document:
            # FIX: Use structural layout sorting instead of raw block coordinates
            # to handle multi-column sections correctly
            page_text = page.get_text("text", sort=True)
            if page_text.strip():
                text += page_text + "\n"

        document.close()
        return text.strip()

    @staticmethod
    def _extract_docx(file_bytes: bytes) -> str:
        document = docx.Document(BytesIO(file_bytes))
        lines = []
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                lines.append(paragraph.text.strip())
        return "\n".join(lines)