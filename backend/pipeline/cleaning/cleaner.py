"""
ATLAS Platform - Data Cleaning Module

Handles HTML removal, whitespace normalization, unicode normalization, encoding cleanup, and language cleanup.
"""

import html
import re
import unicodedata
from typing import Any

from backend.core.logging import get_logger
from backend.pipeline.types import PipelineRecord

logger = get_logger(__name__)


class HTMLCleaner:
    """Removes HTML tags and entities from text."""
    
    # HTML tag pattern
    TAG_PATTERN = re.compile(r"<[^>]+>")
    
    # HTML entity pattern
    ENTITY_PATTERN = re.compile(r"&(\w+);|&#[0-9]+;|&#x[0-9a-fA-F]+;")
    
    # Common HTML tag attributes to preserve
    PRESERVE_ATTRIBUTES = {"href", "src", "alt", "title"}
    
    def remove_html(self, text: str | None) -> str | None:
        """Remove HTML tags from text."""
        if not text:
            return text
        
        # Remove HTML tags
        text = self.TAG_PATTERN.sub(" ", text)
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove extra whitespace
        text = self._normalize_whitespace(text)
        
        return text.strip()
    
    def extract_text_from_html(self, html_content: str | None) -> str | None:
        """Extract plain text from HTML content."""
        if not html_content:
            return None
        
        from bs4 import BeautifulSoup
        
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text(separator=" ", strip=True)
            return self._normalize_whitespace(text).strip()
        except Exception:
            return self.remove_html(html_content)
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text."""
        # Replace multiple spaces with single space
        text = re.sub(r" +", " ", text)
        # Replace newlines with space
        text = re.sub(r"[\n\r\t]+", " ", text)
        return text


class WhitespaceNormalizer:
    """Normalizes whitespace in text."""
    
    def normalize(self, text: str | None) -> str | None:
        """Normalize whitespace in text."""
        if not text:
            return text
        
        # Replace tabs with spaces
        text = text.replace("\t", " ")
        
        # Replace multiple spaces with single space
        text = re.sub(r" +", " ", text)
        
        # Handle newlines
        text = re.sub(r" *\n *", "\n", text)
        
        # Replace multiple newlines with single newline
        text = re.sub(r"\n+", "\n", text)
        
        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)
        
        return text.strip()
    
    def normalize_line_endings(self, text: str | None, style: str = "unix") -> str | None:
        """Normalize line endings to specified style."""
        if not text:
            return text
        
        if style == "unix":
            text = text.replace("\r\n", "\n")
            text = text.replace("\r", "\n")
        elif style == "windows":
            text = text.replace("\r\n", "\n")
            text = text.replace("\r", "\n")
            text = text.replace("\n", "\r\n")
        elif style == "mac":
            text = text.replace("\r\n", "\r")
            text = text.replace("\n", "\r")
        
        return text


class UnicodeNormalizer:
    """Normalizes unicode characters."""
    
    def normalize(
        self,
        text: str | None,
        form: str = "NFKC",
    ) -> str | None:
        """
        Normalize unicode text.
        
        Args:
            text: Text to normalize
            form: Unicode normalization form (NFC, NFD, NFKC, NFKD)
        """
        if not text:
            return text
        
        # Normalize unicode
        text = unicodedata.normalize(form, text)
        
        return text
    
    def to_ascii(self, text: str | None, errors: str = "ignore") -> str | None:
        """Convert text to ASCII, handling errors."""
        if not text:
            return text
        
        try:
            # First normalize
            text = unicodedata.normalize("NFKD", text)
            # Encode to ASCII, then decode
            text = text.encode("ascii", errors=errors).decode("ascii")
        except Exception:
            pass
        
        return text
    
    def fix_mojibake(self, text: str | None) -> str | None:
        """Try to fix common mojibake issues."""
        if not text:
            return text
        
        # Try common encoding fixes
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
        
        for encoding in encodings:
            try:
                # Try to decode as the encoding
                decoded = text.encode("latin-1").decode(encoding)
                # Check if it's valid UTF-8
                decoded.encode("utf-8")
                if decoded != text:
                    return decoded
            except Exception:
                continue
        
        return text


class EncodingCleaner:
    """Cleans encoding issues in text."""
    
    PROBLEMATIC_CHARS = [
        "\x00",  # Null byte
        "\x01",  # SOH
        "\x02",  # STX
        "\x03",  # ETX
        "\x04",  # EOT
        "\x05",  # ENQ
        "\x06",  # ACK
        "\x07",  # Bell
        "\x08",  # Backspace
        "\x0e",  # SO
        "\x0f",  # SI
        "\x10",  # DLE
        "\x11",  # DC1
        "\x12",  # DC2
        "\x13",  # DC3
        "\x14",  # DC4
        "\x15",  # NAK
        "\x16",  # SYN
        "\x17",  # ETB
        "\x18",  # CAN
        "\x19",  # EM
        "\x1a",  # SUB (Ctrl+Z)
        "\x1b",  # ESC
        "\x1c",  # FS
        "\x1d",  # GS
        "\x1e",  # RS
        "\x1f",  # US
        "\x7f",  # DEL
        "\ufffd",  # Replacement character
    ]
    
    def clean(self, text: str | None) -> str | None:
        """Remove problematic control characters."""
        if not text:
            return text
        
        for char in self.PROBLEMATIC_CHARS:
            text = text.replace(char, "")
        
        return text
    
    def remove_zero_width(self, text: str | None) -> str | None:
        """Remove zero-width characters."""
        if not text:
            return text
        
        # Zero-width characters
        zero_width_chars = [
            "\u200b",  # Zero width space
            "\u200c",  # Zero width non-joiner
            "\u200d",  # Zero width joiner
            "\ufeff",  # Zero width no-break space (BOM)
            "\ufdd0",  # Zero width non-joiner (Arabic)
            "\ufdd1",  # Zero width non-joiner (Arabic)
            "\ufdd2",  # Zero width non-joiner (Arabic)
            "\ufdd3",  # Zero width non-joiner (Arabic)
            "\ufdd4",  # Zero width non-joiner (Arabic)
            "\ufdd5",  # Zero width non-joiner (Arabic)
            "\ufdd6",  # Zero width non-joiner (Arabic)
            "\ufdd7",  # Zero width non-joiner (Arabic)
            "\ufdd8",  # Zero width non-joiner (Arabic)
            "\ufdd9",  # Zero width non-joiner (Arabic)
            "\ufdda",  # Zero width non-joiner (Arabic)
            "\ufddb",  # Zero width non-joiner (Arabic)
            "\ufddc",  # Zero width non-joiner (Arabic)
            "\ufddd",  # Zero width non-joiner (Arabic)
            "\ufdde",  # Zero width non-joiner (Arabic)
            "\ufddf",  # Zero width non-joiner (Arabic)
            "\ufef0",  # Zero width non-joiner (Arabic)
            "\ufef1",  # Zero width non-joiner (Arabic)
        ]
        
        for char in zero_width_chars:
            text = text.replace(char, "")
        
        return text


class LanguageCleaner:
    """Cleans and normalizes text for specific languages."""
    
    def clean_english(self, text: str | None) -> str | None:
        """Clean English text."""
        if not text:
            return text
        
        # Fix common typos
        fixes = {
            r"\bi\b": "I",  # Fix lowercase 'i' to 'I'
            r"\bi'm\b": "I'm",
            r"\bi've\b": "I've",
            r"\bi'll\b": "I'll",
            r"\bi'd\b": "I'd",
            r"\bi've\b": "I've",
            r" n't": "n't",  # Fix space before n't
            r" 're": " 're",  # Fix space before 're
            r" 've": " 've",  # Fix space before 've
            r" 'll": " 'll",  # Fix space before 'll
            r" 't": " 't",  # Fix space before 't
            r" 's": " 's",  # Fix space before 's (possessive)
        }
        
        for pattern, replacement in fixes.items():
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def remove_urls(self, text: str | None, replacement: str = "") -> str | None:
        """Remove URLs from text."""
        if not text:
            return text
        
        # Remove URLs
        url_patterns = [
            r"https?://\S+",
            r"www\.\S+",
            r"\S+\.(com|org|net|gov|edu|io|co)\S*",
        ]
        
        for pattern in url_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def remove_emails(self, text: str | None, replacement: str = "") -> str | None:
        """Remove email addresses from text."""
        if not text:
            return text
        
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        text = re.sub(email_pattern, replacement, text)
        
        return text.strip()
    
    def remove_phone_numbers(
        self,
        text: str | None,
        replacement: str = "",
    ) -> str | None:
        """Remove phone numbers from text."""
        if not text:
            return text
        
        phone_patterns = [
            r"\+?\d{1,3}[-.\s]?\(?\d{2,3}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}",
            r"\(\d{3}\)\s*\d{3}-\d{4}",
            r"\d{3}-\d{3}-\d{4}",
        ]
        
        for pattern in phone_patterns:
            text = re.sub(pattern, replacement, text)
        
        return text.strip()


class DataCleaner:
    """Main cleaner that coordinates all cleaning operations."""
    
    def __init__(self):
        self.html_cleaner = HTMLCleaner()
        self.whitespace_normalizer = WhitespaceNormalizer()
        self.unicode_normalizer = UnicodeNormalizer()
        self.encoding_cleaner = EncodingCleaner()
        self.language_cleaner = LanguageCleaner()
    
    def clean_record(self, record: PipelineRecord) -> dict[str, Any]:
        """Clean all text fields in a pipeline record."""
        data = record.validated_data or record.collected_data or {}
        cleaned = {}
        
        text_fields = [
            "title", "description", "content", "text", "summary",
            "author", "body", "article", "headline",
        ]
        
        for field_name, value in data.items():
            if isinstance(value, str):
                # Apply all cleaners
                cleaned_value = self._clean_text(value)
                cleaned[field_name] = cleaned_value
            elif isinstance(value, dict):
                # Recursively clean dict values
                cleaned[field_name] = {
                    k: self._clean_text(v) if isinstance(v, str) else v
                    for k, v in value.items()
                }
            elif isinstance(value, list):
                # Clean list items
                cleaned[field_name] = [
                    self._clean_text(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                cleaned[field_name] = value
        
        return cleaned
    
    def _clean_text(self, text: str) -> str:
        """Apply all cleaning steps to text."""
        # 1. Fix encoding first
        text = self.encoding_cleaner.clean(text)
        text = self.encoding_cleaner.remove_zero_width(text)
        
        # 2. Normalize unicode
        text = self.unicode_normalizer.normalize(text)
        
        # 3. Remove HTML
        text = self.html_cleaner.remove_html(text)
        
        # 4. Normalize whitespace
        text = self.whitespace_normalizer.normalize(text)
        
        # 5. Clean language-specific issues
        text = self.language_cleaner.clean_english(text)
        
        return text.strip()
    
    def clean_field(self, field_name: str, value: str | None) -> str | None:
        """Clean a specific field."""
        if not isinstance(value, str):
            return value
        
        return self._clean_text(value)


# Global cleaner instance
_cleaner: DataCleaner | None = None


def get_cleaner() -> DataCleaner:
    """Get the global data cleaner."""
    global _cleaner
    if _cleaner is None:
        _cleaner = DataCleaner()
    return _cleaner
