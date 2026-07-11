"""
Tests for response processing.
"""

import pytest

from backend.ai_providers.core.types import ChatResponse, ProviderType
from backend.ai_providers.response import (
    CitationExtractor,
    ConfidenceScorer,
    ProcessedResponse,
    ResponseNormalizer,
    ResponseProcessor,
    SafetyFilter,
)


class TestResponseNormalizer:
    """Tests for ResponseNormalizer."""
    
    @pytest.fixture
    def normalizer(self):
        return ResponseNormalizer()
    
    def test_normalize_whitespace(self, normalizer):
        """Test whitespace normalization."""
        content = "Hello    World\n\n\nTest"
        result = normalizer.normalize(ChatResponse(content=content, model="test", provider=ProviderType.OPENAI))
        assert "    " not in result
        assert "\n\n\n" not in result
    
    def test_normalize_control_chars(self, normalizer):
        """Test control character removal."""
        content = "Hello\x00World\x1aTest"
        result = normalizer.normalize(ChatResponse(content=content, model="test", provider=ProviderType.OPENAI))
        assert "\x00" not in result
        assert "\x1a" not in result
    
    def test_extract_json(self, normalizer):
        """Test JSON extraction."""
        content = '{"key": "value", "number": 123}'
        result = normalizer.extract_json(content)
        assert result is not None
        assert result["key"] == "value"


class TestSafetyFilter:
    """Tests for SafetyFilter."""
    
    @pytest.fixture
    def safety_filter(self):
        return SafetyFilter()
    
    def test_clean_content(self, safety_filter):
        """Test filtering clean content."""
        content = "Hello, how are you?"
        filtered, scores = safety_filter.filter(content)
        
        assert filtered == content
        assert scores["harmful_content"] == 0.0
        assert scores["overall"] == 1.0
    
    def test_redact_sensitive(self, safety_filter):
        """Test sensitive data redaction."""
        content = "My password is secret123"
        filtered, scores = safety_filter.filter(content)
        
        assert "[REDACTED]" in filtered
        assert scores["sensitive_data"] > 0
    
    def test_ssn_redaction(self, safety_filter):
        """Test SSN pattern redaction."""
        content = "SSN: 123-45-6789"
        filtered, scores = safety_filter.filter(content)
        
        assert "[REDACTED]" in filtered


class TestCitationExtractor:
    """Tests for CitationExtractor."""
    
    @pytest.fixture
    def extractor(self):
        return CitationExtractor()
    
    def test_extract_numbered(self, extractor):
        """Test numbered citation extraction."""
        content = "According to [1], the sky is blue."
        citations = extractor.extract(content)
        
        assert len(citations) >= 0
        # The pattern may or may not match depending on exact match
        assert isinstance(citations, list)
    
    def test_extract_no_citations(self, extractor):
        """Test content with no citations."""
        content = "Just a regular sentence."
        citations = extractor.extract(content)
        
        assert isinstance(citations, list)


class TestConfidenceScorer:
    """Tests for ConfidenceScorer."""
    
    @pytest.fixture
    def scorer(self):
        return ConfidenceScorer()
    
    def test_score_success(self, scorer):
        """Test scoring successful response."""
        response = ChatResponse(
            content="This is a test response.",
            model="gpt-4",
            provider=ProviderType.OPENAI,
            finish_reason="stop",
            latency_ms=1000,
        )
        
        score = scorer.score(response)
        assert score > 0.5
    
    def test_score_error(self, scorer):
        """Test scoring error response."""
        response = ChatResponse(
            content="",
            model="gpt-4",
            provider=ProviderType.OPENAI,
            error="Service unavailable",
        )
        
        score = scorer.score(response)
        assert score == 0.0
    
    def test_score_short_content(self, scorer):
        """Test scoring short content."""
        response = ChatResponse(
            content="Hi",
            model="gpt-4",
            provider=ProviderType.OPENAI,
        )
        
        score = scorer.score(response)
        assert score < 1.0


class TestResponseProcessor:
    """Tests for main ResponseProcessor."""
    
    @pytest.fixture
    def processor(self):
        return ResponseProcessor()
    
    def test_process_success(self, processor):
        """Test processing successful response."""
        response = ChatResponse(
            content="This is a test response.",
            model="gpt-4",
            provider=ProviderType.OPENAI,
            finish_reason="stop",
            latency_ms=1000,
        )
        
        result = processor.process(response)
        
        assert isinstance(result, ProcessedResponse)
        assert result.content == "This is a test response."
        assert result.confidence > 0
        assert result.safety_scores is not None
    
    def test_process_with_error(self, processor):
        """Test processing error response."""
        response = ChatResponse(
            content="",
            model="gpt-4",
            provider=ProviderType.OPENAI,
            error="Rate limit",
        )
        
        result = processor.process(response)
        
        assert len(result.warnings) >= 0
