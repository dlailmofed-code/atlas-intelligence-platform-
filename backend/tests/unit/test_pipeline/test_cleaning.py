"""
Tests for data cleaning.
"""

import pytest

from backend.pipeline.cleaning import (
    DataCleaner,
    EncodingCleaner,
    HTMLCleaner,
    LanguageCleaner,
    UnicodeNormalizer,
    WhitespaceNormalizer,
)


class TestHTMLCleaner:
    """Tests for HTMLCleaner."""

    @pytest.fixture
    def cleaner(self):
        return HTMLCleaner()

    def test_remove_simple_tags(self, cleaner):
        """Test simple HTML tag removal."""
        result = cleaner.remove_html("<p>Hello World</p>")
        assert "<p>" not in result
        assert "Hello World" in result

    def test_remove_complex_tags(self, cleaner):
        """Test complex HTML tag removal."""
        result = cleaner.remove_html("<div class='test'><span>Text</span></div>")
        assert "<div" not in result
        assert "<span>" not in result
        assert "Text" in result

    def test_decode_entities(self, cleaner):
        """Test HTML entity decoding."""
        result = cleaner.remove_html("Hello &amp; World")
        assert "&amp;" not in result
        assert "Hello" in result

    def test_none_input(self, cleaner):
        """Test None input."""
        result = cleaner.remove_html(None)
        assert result is None

    def test_no_html(self, cleaner):
        """Test text without HTML."""
        result = cleaner.remove_html("Plain text")
        assert result == "Plain text"


class TestWhitespaceNormalizer:
    """Tests for WhitespaceNormalizer."""

    @pytest.fixture
    def normalizer(self):
        return WhitespaceNormalizer()

    def test_normalize_multiple_spaces(self, normalizer):
        """Test multiple space normalization."""
        result = normalizer.normalize("Hello    World")
        assert "    " not in result
        assert "Hello World" in result

    def test_normalize_tabs(self, normalizer):
        """Test tab normalization."""
        result = normalizer.normalize("Hello\tWorld")
        assert "\t" not in result
        assert "Hello World" in result

    def test_normalize_newlines(self, normalizer):
        """Test newline normalization."""
        result = normalizer.normalize("Hello\nWorld")
        assert "\n" in result  # Preserved but single

    def test_normalize_leading_trailing(self, normalizer):
        """Test leading/trailing whitespace."""
        result = normalizer.normalize("  Hello World  ")
        assert result == "Hello World"

    def test_none_input(self, normalizer):
        """Test None input."""
        result = normalizer.normalize(None)
        assert result is None


class TestUnicodeNormalizer:
    """Tests for UnicodeNormalizer."""

    @pytest.fixture
    def normalizer(self):
        return UnicodeNormalizer()

    def test_normalize_nfkc(self, normalizer):
        """Test NFKC normalization."""
        result = normalizer.normalize("café", form="NFKC")
        assert result is not None

    def test_to_ascii(self, normalizer):
        """Test ASCII conversion."""
        result = normalizer.to_ascii("café")
        assert "caf" in result

    def test_none_input(self, normalizer):
        """Test None input."""
        result = normalizer.normalize(None)
        assert result is None


class TestEncodingCleaner:
    """Tests for EncodingCleaner."""

    @pytest.fixture
    def cleaner(self):
        return EncodingCleaner()

    def test_remove_null_bytes(self, cleaner):
        """Test null byte removal."""
        result = cleaner.clean("Hello\x00World")
        assert "\x00" not in result
        assert "HelloWorld" in result

    def test_remove_control_chars(self, cleaner):
        """Test control character removal."""
        result = cleaner.clean("Hello\x01World")
        assert "\x01" not in result

    def test_remove_zero_width(self, cleaner):
        """Test zero-width character removal."""
        result = cleaner.remove_zero_width("Hello\u200bWorld")
        assert "\u200b" not in result

    def test_none_input(self, cleaner):
        """Test None input."""
        result = cleaner.clean(None)
        assert result is None


class TestLanguageCleaner:
    """Tests for LanguageCleaner."""

    @pytest.fixture
    def cleaner(self):
        return LanguageCleaner()

    def test_fix_lowercase_i(self, cleaner):
        """Test lowercase 'i' fix."""
        result = cleaner.clean_english("i am happy")
        assert "I" in result

    def test_fix_contractions(self, cleaner):
        """Test contraction fixes."""
        result = cleaner.clean_english("i'm going")
        assert "I'm" in result

    def test_remove_urls(self, cleaner):
        """Test URL removal."""
        result = cleaner.remove_urls("Visit https://example.com for more")
        assert "https://example.com" not in result

    def test_remove_emails(self, cleaner):
        """Test email removal."""
        result = cleaner.remove_emails("Contact john@example.com")
        assert "john@example.com" not in result

    def test_remove_phone_numbers(self, cleaner):
        """Test phone number removal."""
        result = cleaner.remove_phone_numbers("Call 555-123-4567")
        assert "555-123-4567" not in result


class TestDataCleaner:
    """Tests for main DataCleaner."""

    @pytest.fixture
    def cleaner(self):
        return DataCleaner()

    def test_clean_record(self, cleaner):
        """Test record cleaning."""
        from uuid import uuid4

        from backend.pipeline.types import PipelineRecord, PipelineStage, SourceType

        record = PipelineRecord(
            id=uuid4(),
            source_name="test",
            source_type=SourceType.WEB,
            stage=PipelineStage.COLLECTED,
            validated_data={
                "title": "  Hello   World  ",
                "content": "<p>Test content</p>",
            },
        )

        result = cleaner.clean_record(record)
        assert "  " not in result.get("title", "")
        assert "<p>" not in result.get("content", "")

    def test_clean_field(self, cleaner):
        """Test field cleaning."""
        result = cleaner.clean_field("test", "  Hello  ")
        assert result == "Hello"

    def test_clean_html_in_content(self, cleaner):
        """Test HTML cleaning in content."""
        from uuid import uuid4

        from backend.pipeline.types import PipelineRecord, PipelineStage, SourceType

        record = PipelineRecord(
            id=uuid4(),
            source_name="test",
            source_type=SourceType.WEB,
            stage=PipelineStage.COLLECTED,
            validated_data={
                "content": "<div><p>Article content</p></div>",
            },
        )

        result = cleaner.clean_record(record)
        assert "<div>" not in result.get("content", "")
        assert "Article content" in result.get("content", "")
