"""
ATLAS Platform - Response Processing

Response normalization, safety filtering, and citation extraction.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any

from backend.ai_providers.core.types import ChatResponse


@dataclass
class ProcessedResponse:
    """Processed AI response with metadata."""
    
    content: str
    confidence: float
    citations: list[dict[str, Any]] = field(default_factory=list)
    safety_scores: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


class ResponseNormalizer:
    """Normalizes AI responses."""
    
    def normalize(self, response: ChatResponse) -> str:
        """Normalize response content."""
        content = response.content
        
        # Remove extra whitespace
        content = re.sub(r"\s+", " ", content)
        
        # Remove control characters
        content = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", content)
        
        # Trim
        content = content.strip()
        
        return content
    
    def extract_json(self, content: str) -> dict | None:
        """Extract JSON from response content."""
        # Try to find JSON in the content
        json_patterns = [
            r"\{[^{}]*\}",
            r"\[[^\[\]]*\]",
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        return None


class SafetyFilter:
    """Filters and scores response safety."""
    
    HARMFUL_PATTERNS = [
        (r"\b(hack|exploit|attack)\b", 0.8),
        (r"\b(inject|steal|phish)\b", 0.7),
        (r"\b(destroy|harm|kill)\b", 0.6),
    ]
    
    SENSITIVE_PATTERNS = [
        r"\b(password|secret|api.?key)\b",
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
        r"\b\d{16}\b",  # Credit card pattern
    ]
    
    def filter(self, content: str) -> tuple[str, dict[str, float]]:
        """
        Filter content and return safety scores.
        
        Returns:
            Tuple of (filtered_content, safety_scores)
        """
        safety_scores = {
            "harmful_content": 0.0,
            "sensitive_data": 0.0,
            "overall": 1.0,
        }
        
        filtered = content
        
        # Check for harmful content
        for pattern, severity in self.HARMFUL_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                safety_scores["harmful_content"] = max(
                    safety_scores["harmful_content"],
                    severity
                )
        
        # Check for sensitive data
        for pattern in self.SENSITIVE_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                safety_scores["sensitive_data"] = 0.7
                # Redact sensitive data
                for match in matches:
                    filtered = filtered.replace(match, "[REDACTED]")
        
        # Calculate overall score
        safety_scores["overall"] = 1.0 - (
            safety_scores["harmful_content"] * 0.5 +
            safety_scores["sensitive_data"] * 0.5
        )
        
        return filtered, safety_scores


class CitationExtractor:
    """Extracts citations from responses."""
    
    CITATION_PATTERNS = [
        (r"\[(\d+)\]", "numbered"),  # [1], [2], etc.
        (r"\(([^)]+\.pdf)\)", "document"),  # (document.pdf)
        (r"source:\s*([^\s]+)", "url"),  # source: url
        (r"according to\s+([^\.]+)", "reference"),  # according to...
    ]
    
    def extract(self, content: str) -> list[dict[str, Any]]:
        """Extract citations from response."""
        citations = []
        
        for pattern, cit_type in self.CITATION_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                citation = {
                    "type": cit_type,
                    "value": match.group(1) if match.groups() else match.group(0),
                    "position": match.start(),
                }
                citations.append(citation)
        
        return citations


class ConfidenceScorer:
    """Scores response confidence."""
    
    def score(self, response: ChatResponse) -> float:
        """Calculate confidence score for a response."""
        score = 1.0
        
        # Penalize for errors
        if response.error:
            return 0.0
        
        # Penalize for short responses
        if len(response.content) < 10:
            score *= 0.8
        
        # Penalize for high latency
        if response.latency_ms > 30000:
            score *= 0.9
        
        # Penalize for missing usage data
        if not response.usage:
            score *= 0.95
        
        # Bonus for finish reason
        if response.finish_reason == "stop":
            score *= 1.0
        elif response.finish_reason == "length":
            score *= 0.9
        
        return max(0.0, min(1.0, score))


class ResponseProcessor:
    """Main response processor combining all components."""
    
    def __init__(self):
        self.normalizer = ResponseNormalizer()
        self.safety_filter = SafetyFilter()
        self.citation_extractor = CitationExtractor()
        self.confidence_scorer = ConfidenceScorer()
    
    def process(self, response: ChatResponse) -> ProcessedResponse:
        """
        Process an AI response.
        
        Args:
            response: Raw response from provider
            
        Returns:
            ProcessedResponse with normalized content, safety scores, etc.
        """
        warnings = []
        
        # Normalize content
        content = self.normalizer.normalize(response)
        
        # Filter for safety
        content, safety_scores = self.safety_filter.filter(content)
        
        # Extract citations
        citations = self.citation_extractor.extract(content)
        
        # Calculate confidence
        confidence = self.confidence_scorer.score(response)
        
        # Add warnings for issues
        if response.error:
            warnings.append(f"Provider error: {response.error}")
        
        if not response.usage:
            warnings.append("No token usage data available")
        
        if len(content) < 10:
            warnings.append("Response content is very short")
        
        return ProcessedResponse(
            content=content,
            confidence=confidence,
            citations=citations,
            safety_scores=safety_scores,
            metadata={
                "model": response.model,
                "provider": response.provider.value if response.provider else "unknown",
                "finish_reason": response.finish_reason,
                "latency_ms": response.latency_ms,
            },
            warnings=warnings,
        )
    
    def extract_structured_output(
        self,
        response: ChatResponse,
        schema: dict | None = None,
    ) -> dict | None:
        """Extract structured output (JSON) from response."""
        content = self.normalizer.normalize(response)
        return self.normalizer.extract_json(content)


# Global processor instance
_processor: ResponseProcessor | None = None


def get_response_processor() -> ResponseProcessor:
    """Get the global response processor."""
    global _processor
    if _processor is None:
        _processor = ResponseProcessor()
    return _processor
