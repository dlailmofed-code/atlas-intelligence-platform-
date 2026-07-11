"""
ATLAS Platform - Data Validation Module

Handles schema validation, source validation, confidence scoring, and malformed record detection.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, ValidationError, create_model

from backend.core.logging import get_logger
from backend.pipeline.types import PipelineRecord, SourceType, ValidationResult

logger = get_logger(__name__)


@dataclass
class FieldValidationRule:
    """Rule for validating a field."""
    
    field_name: str
    field_type: type | None = None
    required: bool = False
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    allowed_values: list[Any] | None = None
    custom_validator: str | None = None  # Name of custom validation method


@dataclass
class SchemaDefinition:
    """Schema definition for validation."""
    
    name: str
    source_type: SourceType
    required_fields: list[str] = field(default_factory=list)
    optional_fields: list[str] = field(default_factory=list)
    field_rules: list[FieldValidationRule] = field(default_factory=list)
    confidence_weights: dict[str, float] = field(default_factory=dict)


class SchemaValidator:
    """Validates records against schema definitions."""
    
    def __init__(self):
        self._schemas: dict[str, SchemaDefinition] = {}
        self._init_default_schemas()
    
    def _init_default_schemas(self) -> None:
        """Initialize default schema definitions."""
        # News schema
        self.register_schema(
            SchemaDefinition(
                name="news",
                source_type=SourceType.NEWS,
                required_fields=["title", "url"],
                optional_fields=["description", "content", "author", "published_at", "source"],
                field_rules=[
                    FieldValidationRule(
                        field_name="url",
                        pattern=r"^https?://",
                        required=True,
                    ),
                    FieldValidationRule(
                        field_name="title",
                        min_length=5,
                        max_length=500,
                        required=True,
                    ),
                    FieldValidationRule(
                        field_name="published_at",
                        pattern=r"^\d{4}-\d{2}-\d{2}",
                    ),
                ],
                confidence_weights={
                    "title": 0.3,
                    "url": 0.2,
                    "description": 0.15,
                    "content": 0.2,
                    "author": 0.05,
                    "published_at": 0.1,
                },
            )
        )
        
        # Financial schema
        self.register_schema(
            SchemaDefinition(
                name="financial",
                source_type=SourceType.FINANCIAL,
                required_fields=["symbol", "price"],
                optional_fields=["change", "volume", "timestamp", "high", "low", "open"],
                field_rules=[
                    FieldValidationRule(
                        field_name="symbol",
                        pattern=r"^[A-Z]{1,5}$",
                        required=True,
                    ),
                    FieldValidationRule(
                        field_name="price",
                        field_type=(int, float),
                        required=True,
                    ),
                    FieldValidationRule(
                        field_name="volume",
                        field_type=int,
                    ),
                ],
                confidence_weights={
                    "symbol": 0.2,
                    "price": 0.3,
                    "change": 0.1,
                    "volume": 0.1,
                    "timestamp": 0.15,
                    "high": 0.075,
                    "low": 0.075,
                },
            )
        )
        
        # Government schema
        self.register_schema(
            SchemaDefinition(
                name="government",
                source_type=SourceType.GOVERNMENT,
                required_fields=["title", "date"],
                optional_fields=["description", "source_url", "category"],
                field_rules=[
                    FieldValidationRule(
                        field_name="date",
                        pattern=r"^\d{4}-\d{2}-\d{2}",
                        required=True,
                    ),
                    FieldValidationRule(
                        field_name="title",
                        min_length=3,
                        required=True,
                    ),
                ],
                confidence_weights={
                    "title": 0.4,
                    "date": 0.3,
                    "description": 0.15,
                    "source_url": 0.1,
                    "category": 0.05,
                },
            )
        )
    
    def register_schema(self, schema: SchemaDefinition) -> None:
        """Register a schema definition."""
        self._schemas[schema.name] = schema
        self._schemas[schema.source_type.value] = schema
        logger.debug(
            "Schema registered",
            extra={"schema_name": schema.name}
        )
    
    def get_schema(self, name_or_type: str) -> SchemaDefinition | None:
        """Get a schema by name or source type."""
        return self._schemas.get(name_or_type)
    
    def validate_record(
        self,
        record: PipelineRecord,
        schema_name: str | None = None,
    ) -> ValidationResult:
        """
        Validate a pipeline record against a schema.
        
        Args:
            record: The record to validate
            schema_name: Optional schema name, otherwise inferred from source_type
            
        Returns:
            ValidationResult with validation status and errors
        """
        schema = self._schemas.get(schema_name or record.source_type.value)
        
        if not schema:
            return ValidationResult(
                is_valid=True,
                confidence_score=0.5,
                warnings=[f"No schema found for: {schema_name or record.source_type.value}"],
            )
        
        data = record.collected_data or record.raw_data or {}
        errors = []
        warnings = []
        field_scores = []
        
        # Check required fields
        for field_name in schema.required_fields:
            if field_name not in data or data[field_name] is None:
                errors.append(f"Required field missing: {field_name}")
            else:
                field_scores.append(field_name)
        
        # Validate field rules
        for rule in schema.field_rules:
            value = data.get(rule.field_name)
            
            if value is None:
                if rule.required:
                    errors.append(f"Required field is null: {rule.field_name}")
                continue
            
            # Type validation
            if rule.field_type and not isinstance(value, rule.field_type):
                errors.append(
                    f"Invalid type for {rule.field_name}: "
                    f"expected {rule.field_type}, got {type(value)}"
                )
            
            # Length validation
            if isinstance(value, str):
                if rule.min_length and len(value) < rule.min_length:
                    errors.append(
                        f"Field {rule.field_name} too short: "
                        f"min {rule.min_length}, got {len(value)}"
                    )
                if rule.max_length and len(value) > rule.max_length:
                    errors.append(
                        f"Field {rule.field_name} too long: "
                        f"max {rule.max_length}, got {len(value)}"
                    )
                
                # Pattern validation
                if rule.pattern:
                    if not re.match(rule.pattern, value):
                        errors.append(
                            f"Field {rule.field_name} does not match pattern: {rule.pattern}"
                        )
            
            # Allowed values validation
            if rule.allowed_values and value not in rule.allowed_values:
                errors.append(
                    f"Field {rule.field_name} has invalid value: "
                    f"{value} not in {rule.allowed_values}"
                )
            
            field_scores.append(rule.field_name)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(
            schema, field_scores, data
        )
        
        is_valid = len(errors) == 0
        
        if is_valid and len(warnings) == 0:
            logger.debug(
                "Record validated",
                extra={
                    "record_id": str(record.id),
                    "confidence": confidence_score,
                }
            )
        
        return ValidationResult(
            is_valid=is_valid,
            confidence_score=confidence_score,
            errors=errors,
            warnings=warnings,
            validated_data=data if is_valid else None,
        )
    
    def _calculate_confidence(
        self,
        schema: SchemaDefinition,
        field_scores: list[str],
        data: dict[str, Any],
    ) -> float:
        """Calculate confidence score based on field presence and quality."""
        if not schema.confidence_weights:
            # Equal weights if not defined
            total_fields = len(schema.required_fields) + len(schema.optional_fields)
            present_fields = len(field_scores)
            return present_fields / total_fields if total_fields > 0 else 0.0
        
        total_weight = sum(schema.confidence_weights.values())
        achieved_weight = 0.0
        
        for field_name in field_scores:
            weight = schema.confidence_weights.get(field_name, 0)
            achieved_weight += weight
            
            # Additional quality checks
            value = data.get(field_name)
            if value and isinstance(value, str):
                # Penalize very short values
                if len(value) < 10:
                    weight *= 0.8
                # Bonus for well-formed values
                if len(value) > 50:
                    weight *= 1.1
        
        confidence = achieved_weight / total_weight if total_weight > 0 else 0.0
        
        # Ensure within bounds
        return max(0.0, min(1.0, confidence))


class SourceValidator:
    """Validates data sources and their authenticity."""
    
    def __init__(self):
        self._known_sources: dict[str, dict[str, Any]] = {}
        self._source_reliability: dict[str, float] = {}
    
    def register_source(
        self,
        source_name: str,
        source_type: SourceType,
        base_url: str | None = None,
        reliability_score: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a known data source."""
        self._known_sources[source_name] = {
            "source_type": source_type,
            "base_url": base_url,
            "reliability_score": reliability_score,
            "metadata": metadata or {},
        }
        self._source_reliability[source_name] = reliability_score
    
    def validate_source(self, record: PipelineRecord) -> ValidationResult:
        """Validate the source of a record."""
        errors = []
        warnings = []
        confidence = 0.5
        
        source_name = record.source_name
        data = record.raw_data or record.collected_data or {}
        
        # Check if source is known
        if source_name not in self._known_sources:
            warnings.append(f"Unknown source: {source_name}")
            confidence *= 0.8
        else:
            source_info = self._known_sources[source_name]
            confidence *= source_info["reliability_score"]
            
            # Verify source type matches
            if source_info["source_type"] != record.source_type:
                warnings.append(
                    f"Source type mismatch: expected {source_info['source_type']}, "
                    f"got {record.source_type}"
                )
                confidence *= 0.9
            
            # Verify URL if present
            if "url" in data:
                url = data["url"]
                base_url = source_info.get("base_url")
                
                if base_url and not self._verify_url_domain(url, base_url):
                    warnings.append(f"URL does not match source domain: {url}")
                    confidence *= 0.9
        
        # Validate URL format if present
        if "url" in data:
            url = data["url"]
            if not self._is_valid_url(url):
                errors.append(f"Invalid URL format: {url}")
                confidence *= 0.5
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            confidence_score=confidence,
            errors=errors,
            warnings=warnings,
        )
    
    def _verify_url_domain(self, url: str, expected_domain: str) -> bool:
        """Verify URL domain matches expected domain."""
        try:
            parsed = urlparse(url)
            expected_parsed = urlparse(expected_domain)
            return parsed.netloc == expected_parsed.netloc
        except Exception:
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False


class MalformedRecordDetector:
    """Detects malformed or suspicious records."""
    
    def __init__(self):
        self._spam_patterns = [
            r"(?i)click\s+here",
            r"(?i)buy\s+now",
            r"(?i)limited\s+time",
            r"(?i)act\s+now",
            r"(?i)free\s+money",
            r"(?i)winner",
            r"(?i)congratulations",
            r"<script[^>]*>",
            r"javascript:",
            r"onclick\s*=",
        ]
        self._encoding_issues = [
            "\ufffd",
            "\x00",
            "\x1a",
        ]
    
    def detect(
        self,
        record: PipelineRecord,
    ) -> tuple[bool, list[str]]:
        """
        Detect malformed records.
        
        Args:
            record: The record to check
            
        Returns:
            Tuple of (is_malformed, issues)
        """
        issues = []
        data = record.raw_data or record.collected_data or {}
        
        # Check for spam patterns
        for pattern in self._spam_patterns:
            for field_name in ["title", "description", "content"]:
                value = data.get(field_name, "")
                if value and isinstance(value, str):
                    if re.search(pattern, value):
                        issues.append(f"Spam pattern detected in {field_name}")
        
        # Check for encoding issues
        for issue_char in self._encoding_issues:
            for field_name, value in data.items():
                if value and isinstance(value, str):
                    if issue_char in value:
                        issues.append(f"Encoding issue in {field_name}")
        
        # Check for empty required fields
        if not any(data.get(f) for f in ["title", "content", "description"]):
            issues.append("No content fields present")
        
        # Check for excessive special characters
        for field_name in ["title", "content"]:
            value = data.get(field_name, "")
            if value and isinstance(value, str):
                special_char_ratio = len(re.findall(r"[^\w\s]", value)) / len(value)
                if special_char_ratio > 0.3:
                    issues.append(f"Excessive special characters in {field_name}")
        
        # Check for gibberish (very short random strings)
        for field_name in ["title", "description"]:
            value = data.get(field_name, "")
            if value and isinstance(value, str):
                if len(value) > 0 and len(value) < 5:
                    if not value.replace(" ", "").isalpha():
                        issues.append(f"Possible gibberish in {field_name}")
        
        is_malformed = len(issues) > 0
        
        if is_malformed:
            logger.warning(
                "Malformed record detected",
                extra={"record_id": str(record.id), "issues": issues}
            )
        
        return is_malformed, issues


# Global validator instances
_schema_validator: SchemaValidator | None = None
_source_validator: SourceValidator | None = None
_malformed_detector: MalformedRecordDetector | None = None


def get_schema_validator() -> SchemaValidator:
    """Get the global schema validator."""
    global _schema_validator
    if _schema_validator is None:
        _schema_validator = SchemaValidator()
    return _schema_validator


def get_source_validator() -> SourceValidator:
    """Get the global source validator."""
    global _source_validator
    if _source_validator is None:
        _source_validator = SourceValidator()
    return _source_validator


def get_malformed_detector() -> MalformedRecordDetector:
    """Get the global malformed record detector."""
    global _malformed_detector
    if _malformed_detector is None:
        _malformed_detector = MalformedRecordDetector()
    return _malformed_detector
