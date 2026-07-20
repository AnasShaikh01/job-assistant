import fitz
import docx
from io import BytesIO
from pathlib import Path
from dataclasses import dataclass, field
from typing import Set, Optional, List

@dataclass
class ExtractionMetadata:
    pages: Optional[int]
    word_count: int
    is_scanned: bool
    file_extension: str

@dataclass
class ExtractionResult:
    text: str
    metadata: ExtractionMetadata
    embedded_links: List[str] = field(default_factory=list)

class ResumeExtractor:
    """
    Pure I/O layer responsible for reading files, preserving logical order, 
    and returning raw text alongside metadata and embedded hyperlinks.
    """
    SUPPORTED_EXTENSIONS: Set[str] = {".pdf", ".docx", ".txt"}
    SCANNED_WORDS_PER_PAGE_THRESHOLD: int = 40

    @classmethod
    def extract(cls, file_bytes: bytes, filename: str) -> ExtractionResult:
        extension = Path(filename).suffix.lower()

        if extension not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")

        if extension == ".pdf":
            return cls._extract_pdf(file_bytes, extension)
        if extension == ".docx":
            return cls._extract_docx(file_bytes, extension)

        return cls._extract_txt(file_bytes, extension)

    @classmethod
    def _normalize_url(cls, uri: str) -> Optional[str]:
        """Filters out non-web links and normalizes valid URLs."""
        if not uri:
            return None
            
        uri = uri.strip()
        
        # Explicitly ignore mailto:, tel:, and internal document references
        if not uri.startswith(("http://", "https://", "www.")):
            return None
            
        if uri.startswith("www."):
            uri = f"https://{uri}"
            
        # Strip trailing slashes and common punctuation often caught in extraction
        return uri.rstrip("/.,;)'\"")

    @classmethod
    def _extract_pdf(cls, file_bytes: bytes, extension: str) -> ExtractionResult:
        text_blocks = []
        embedded_links: Set[str] = set()
        word_count = 0
        
        with fitz.open(stream=file_bytes, filetype="pdf") as document:
            num_pages = len(document)
            for page in document:
                page_text = page.get_text("text", sort=True)
                if page_text.strip():
                    text_blocks.append(page_text)
                    word_count += len(page_text.split())
                
                # Extract and normalize hidden hyperlinks
                for link in page.get_links():
                    uri = cls._normalize_url(link.get("uri", ""))
                    if uri:
                        embedded_links.add(uri)

        full_text = "\n".join(text_blocks).strip()
        
        average_words = word_count / max(num_pages, 1)
        is_scanned = (
            num_pages > 0 
            and word_count > 0 
            and average_words < cls.SCANNED_WORDS_PER_PAGE_THRESHOLD
        )

        metadata = ExtractionMetadata(
            pages=num_pages,
            word_count=word_count,
            is_scanned=is_scanned,
            file_extension=extension
        )
        return ExtractionResult(
            text=full_text, 
            metadata=metadata, 
            embedded_links=sorted(embedded_links)
        )

    @classmethod
    def _extract_docx(cls, file_bytes: bytes, extension: str) -> ExtractionResult:
        document = docx.Document(BytesIO(file_bytes))
        text_blocks = [p.text for p in document.paragraphs if p.text.strip()]
        
        full_text = "\n".join(text_blocks)
        word_count = len(full_text.split())
        
        embedded_links: Set[str] = set()
        
        # Traverse DOCX relationships to find external hyperlinks
        for rel in document.part.rels.values():
            if rel.reltype.endswith("/hyperlink"):
                uri = cls._normalize_url(rel.target_ref)
                if uri:
                    embedded_links.add(uri)
        
        metadata = ExtractionMetadata(
            pages=None,
            word_count=word_count,
            is_scanned=False,
            file_extension=extension
        )
        return ExtractionResult(
            text=full_text, 
            metadata=metadata, 
            embedded_links=sorted(embedded_links)
        )

    @classmethod
    def _extract_txt(cls, file_bytes: bytes, extension: str) -> ExtractionResult:
        full_text = file_bytes.decode("utf-8", errors="ignore").strip()
        word_count = len(full_text.split())
        
        metadata = ExtractionMetadata(
            pages=1,
            word_count=word_count,
            is_scanned=False,
            file_extension=extension
        )
        return ExtractionResult(
            text=full_text, 
            metadata=metadata, 
            embedded_links=[]
        )