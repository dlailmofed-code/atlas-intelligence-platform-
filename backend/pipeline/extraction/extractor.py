"""
ATLAS Platform - Evidence Extraction Module

Extracts entities and evidence from records:
- Companies
- Organizations
- People
- Products
- Countries
- Industries
- Technologies
- Financial values
- Percentages
- Dates
- Events
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from backend.core.logging import get_logger
from backend.pipeline.types import EntityType, ExtractedEvidence, PipelineRecord

logger = get_logger(__name__)


@dataclass
class EntityMatch:
    """A matched entity in text."""
    
    entity_type: EntityType
    text: str
    normalized_text: str
    confidence: float
    start_pos: int
    end_pos: int
    context: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)


class EntityExtractor:
    """Extracts entities from text."""
    
    # Company patterns
    COMPANY_PATTERNS = [
        r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\s+(?:Inc|Corp|Corporation|LLC|Ltd|Limited|Company|Co)\.?)",
        r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\s+(?:Group|Holdings|Partners|Associates|Enterprises|Ventures)\b)",
        r"\b([A-Z][a-zA-Z]+)\s+(?:International|Global|Technologies|Industries|Services)\b",
    ]
    
    # Person patterns
    PERSON_PATTERNS = [
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b",  # Basic name pattern
        r"\b(?:Mr|Mrs|Ms|Miss|Dr|Prof)\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b",
    ]
    
    # Product patterns
    PRODUCT_PATTERNS = [
        r"\b(?:the\s+)?([A-Z][a-z0-9]+(?:\s+[A-Z][a-z0-9]+)*)\s+(?:product|platform|service|solution|app|software|tool)\b",
        r"\b([A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+)\b",  # CamelCase words
    ]
    
    # Country patterns (common)
    COUNTRY_PATTERNS = [
        r"\b(?:United\s+States|United\s+Kingdom|United\s+Arab\s+Emirates|South\s+Korea|North\s+Korea)\b",
        r"\b(?:New\s+Zealand|New\s+Zealand)\b",
        r"\b(?:Saudi\s+Arabia|South\s+Africa|South\s+Africa)\b",
        r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b",
    ]
    
    # Technology patterns
    TECH_PATTERNS = [
        r"\b(?:AI|ML|NLP|CV|CNN|RNN|LLM|GPT|BERT|transformer)\b",
        r"\b(?:Python|Java|JavaScript|TypeScript|Rust|Go|Swift|Kotlin)\b",
        r"\b(?:React|Angular|Vue|Node|Django|Flask|Spring|Rails)\b",
        r"\b(?:AWS|Azure|GCP|Kubernetes|Docker|Terraform|Ansible)\b",
        r"\b(?:Machine\s+Learning|Natural\s+Language\s+Processing|Computer\s+Vision|Deep\s+Learning)\b",
        r"\b(?:Cloud|Edge|On-premises|Hybrid)\b",
    ]
    
    # Industry patterns
    INDUSTRY_PATTERNS = [
        r"\b(?:Fintech|Healthtech|Edtech|Agtech|Proptech|Cleantech|Medtech|Biotech)\b",
        r"\b(?:Financial\s+Services|Healthcare|Education|Agriculture|Real\s+Estate|Manufacturing)\b",
        r"\b(?:Retail|Healthcare|Technology|Energy|Transportation|Entertainment|Media)\b",
    ]
    
    # Financial value patterns
    FINANCIAL_PATTERNS = [
        r"\$\d+(?:,\d{3})*(?:\.\d{2})?(?:\s*(?:million|billion|trillion|thousand))?",
        r"\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|JPY|CNY|INR|KRW)",
        r"(?:€|£|¥|₹|₩)\d+(?:,\d{3})*(?:\.\d{2})?",
        r"\d+(?:\.\d+)?\s*(?:percent|%|percentage)",
    ]
    
    # Event patterns
    EVENT_PATTERNS = [
        r"\b(?:acquisition|merger|takeover|buyout|IPO|launch|announcement|partnership|deal)\b",
        r"\b(?:conference|summit|forum|exhibition|trade\s+show|event)\b",
        r"\b(?:announced|revealed|launched|unveiled|introduced|revealed)\b",
    ]
    
    def __init__(self):
        self._company_cache: dict[str, str] = {}
        self._person_cache: dict[str, str] = {}
    
    def extract_all(self, text: str) -> list[EntityMatch]:
        """Extract all entities from text."""
        entities = []
        
        entities.extend(self._extract_companies(text))
        entities.extend(self._extract_people(text))
        entities.extend(self._extract_technologies(text))
        entities.extend(self._extract_industries(text))
        entities.extend(self._extract_events(text))
        
        return entities
    
    def _extract_companies(self, text: str) -> list[EntityMatch]:
        """Extract company names."""
        matches = []
        
        for pattern in self.COMPANY_PATTERNS:
            for match in re.finditer(pattern, text):
                name = match.group(1)
                normalized = name.lower().strip()
                
                # Skip if in cache with different form
                if normalized in self._company_cache:
                    continue
                
                self._company_cache[normalized] = name
                
                # Extract context
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end]
                
                matches.append(EntityMatch(
                    entity_type=EntityType.COMPANY,
                    text=name,
                    normalized_text=normalized,
                    confidence=0.8,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    context=context,
                ))
        
        return matches
    
    def _extract_people(self, text: str) -> list[EntityMatch]:
        """Extract person names."""
        matches = []
        
        for pattern in self.PERSON_PATTERNS:
            for match in re.finditer(pattern, text):
                name = match.group(1) if match.groups() else match.group(0)
                
                # Skip short names
                if len(name.split()) < 2:
                    continue
                
                normalized = name.lower().strip()
                
                # Skip if looks like company
                skip_words = ["Inc", "Corp", "LLC", "Ltd", "Group", "Company"]
                if any(word in name for word in skip_words):
                    continue
                
                if normalized in self._person_cache:
                    continue
                
                self._person_cache[normalized] = name
                
                # Extract context
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end]
                
                matches.append(EntityMatch(
                    entity_type=EntityType.PERSON,
                    text=name,
                    normalized_text=normalized,
                    confidence=0.7,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    context=context,
                ))
        
        return matches
    
    def _extract_technologies(self, text: str) -> list[EntityMatch]:
        """Extract technology mentions."""
        matches = []
        
        for pattern in self.TECH_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                tech = match.group(0)
                
                matches.append(EntityMatch(
                    entity_type=EntityType.TECHNOLOGY,
                    text=tech,
                    normalized_text=tech.lower(),
                    confidence=0.9,
                    start_pos=match.start(),
                    end_pos=match.end(),
                ))
        
        return matches
    
    def _extract_industries(self, text: str) -> list[EntityMatch]:
        """Extract industry mentions."""
        matches = []
        
        for pattern in self.INDUSTRY_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                industry = match.group(0)
                
                matches.append(EntityMatch(
                    entity_type=EntityType.INDUSTRY,
                    text=industry,
                    normalized_text=industry.lower(),
                    confidence=0.85,
                    start_pos=match.start(),
                    end_pos=match.end(),
                ))
        
        return matches
    
    def _extract_events(self, text: str) -> list[EntityMatch]:
        """Extract event mentions."""
        matches = []
        
        for pattern in self.EVENT_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                event = match.group(0)
                
                matches.append(EntityMatch(
                    entity_type=EntityType.EVENT,
                    text=event,
                    normalized_text=event.lower(),
                    confidence=0.75,
                    start_pos=match.start(),
                    end_pos=match.end(),
                ))
        
        return matches


class ValueExtractor:
    """Extracts financial values, percentages, and dates."""
    
    # Currency patterns
    CURRENCY_PATTERN = r"\$\d+(?:,\d{3})*(?:\.\d{2})?(?:\s*(?:million|billion|trillion|thousand|k|m|b|t))?"
    
    # Percentage patterns
    PERCENTAGE_PATTERN = r"\d+(?:\.\d+)?\s*(?:%|percent|percentage|per\s+cent)"
    
    # Date patterns
    DATE_PATTERNS = [
        (r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"),
        (r"\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}", "%d %b %Y"),
        (r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}", "%b %d, %Y"),
    ]
    
    def extract_financial_values(self, text: str) -> list[dict[str, Any]]:
        """Extract financial values from text."""
        values = []
        
        # Extract currency amounts
        for match in re.finditer(self.CURRENCY_PATTERN, text, re.IGNORECASE):
            value_text = match.group(0)
            value, multiplier = self._parse_currency(value_text)
            
            if value:
                values.append({
                    "type": "currency",
                    "text": value_text,
                    "value": value,
                    "multiplier": multiplier,
                    "normalized_value": value * multiplier,
                    "confidence": 0.9,
                })
        
        # Extract percentages
        for match in re.finditer(self.PERCENTAGE_PATTERN, text, re.IGNORECASE):
            pct_text = match.group(0)
            pct_value = self._parse_percentage(pct_text)
            
            if pct_value is not None:
                values.append({
                    "type": "percentage",
                    "text": pct_text,
                    "value": pct_value,
                    "confidence": 0.9,
                })
        
        return values
    
    def extract_dates(self, text: str) -> list[dict[str, Any]]:
        """Extract dates from text."""
        dates = []
        
        for pattern, fmt in self.DATE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                date_text = match.group(0)
                
                try:
                    dt = datetime.strptime(date_text, fmt)
                    dates.append({
                        "type": "date",
                        "text": date_text,
                        "datetime": dt.isoformat(),
                        "confidence": 0.85,
                    })
                except ValueError:
                    continue
        
        return dates
    
    def _parse_currency(self, text: str) -> tuple[float | None, float]:
        """Parse currency text to numeric value."""
        text = text.strip()
        
        # Get multiplier
        multiplier = 1.0
        multipliers = {
            "thousand": 1000,
            "k": 1000,
            "million": 1000000,
            "m": 1000000,
            "billion": 1000000000,
            "b": 1000000000,
            "trillion": 1000000000000,
            "t": 1000000000000,
        }
        
        for suffix, mult in multipliers.items():
            if suffix in text.lower():
                multiplier = mult
                text = re.sub(suffix, "", text, flags=re.IGNORECASE)
                break
        
        # Extract numeric value
        text = re.sub(r"[$,€£¥₹]", "", text)
        
        try:
            value = float(text.strip())
            return value, multiplier
        except ValueError:
            return None, multiplier
    
    def _parse_percentage(self, text: str) -> float | None:
        """Parse percentage text to numeric value."""
        text = text.strip()
        
        # Remove percentage symbols and words
        text = re.sub(r"%|percent|percentage|per\s+cent", "", text, flags=re.IGNORECASE)
        
        try:
            return float(text.strip())
        except ValueError:
            return None


class EvidenceExtractor:
    """
    Main evidence extractor that coordinates all extraction operations.
    """
    
    def __init__(self):
        self.entity_extractor = EntityExtractor()
        self.value_extractor = ValueExtractor()
    
    def extract_evidence(
        self,
        record: PipelineRecord,
    ) -> list[ExtractedEvidence]:
        """
        Extract all evidence from a record.
        
        Args:
            record: The record to extract evidence from
            
        Returns:
            List of ExtractedEvidence objects
        """
        data = record.deduplicated_data or record.normalized_data or {}
        evidence = []
        
        # Combine text fields for extraction
        text_fields = []
        for field_name in ["title", "description", "content", "summary"]:
            if data.get(field_name):
                text_fields.append(str(data[field_name]))
        
        full_text = " ".join(text_fields)
        
        # Extract entities
        entity_matches = self.entity_extractor.extract_all(full_text)
        
        for match in entity_matches:
            # Determine source field
            source_field = self._get_source_field(data, match.start_pos)
            
            evidence.append(ExtractedEvidence(
                entity_type=match.entity_type,
                entity_id=self._generate_entity_id(match.entity_type, match.normalized_text),
                entity_name=match.text,
                confidence=match.confidence,
                source_record_id=record.id,
                source_field=source_field,
                context=match.context,
                properties={
                    "normalized_name": match.normalized_text,
                },
            ))
        
        # Extract financial values
        financial_values = self.value_extractor.extract_financial_values(full_text)
        
        for fv in financial_values:
            evidence.append(ExtractedEvidence(
                entity_type=EntityType.COMPANY if fv["type"] == "currency" else EntityType.COMPANY,
                entity_id=f"value_{fv['normalized_value']}" if "normalized_value" in fv else f"pct_{fv['value']}",
                entity_name=fv["text"],
                confidence=fv["confidence"],
                source_record_id=record.id,
                source_field="content",
                properties=fv,
            ))
        
        # Extract dates
        dates = self.value_extractor.extract_dates(full_text)
        
        for dt in dates:
            evidence.append(ExtractedEvidence(
                entity_type=EntityType.EVENT,
                entity_id=f"date_{dt['datetime']}",
                entity_name=dt["text"],
                confidence=dt["confidence"],
                source_record_id=record.id,
                source_field="content",
                properties={"datetime": dt["datetime"]},
            ))
        
        logger.info(
            "Evidence extracted",
            extra={
                "record_id": str(record.id),
                "evidence_count": len(evidence),
            }
        )
        
        return evidence
    
    def _generate_entity_id(self, entity_type: EntityType, name: str) -> str:
        """Generate a unique entity ID."""
        import hashlib
        id_string = f"{entity_type.value}:{name}"
        return hashlib.md5(id_string.encode()).hexdigest()[:16]
    
    def _get_source_field(self, data: dict[str, Any], pos: int) -> str:
        """Determine which field an entity came from."""
        for field_name in ["title", "description", "content"]:
            if field_name in data:
                value = str(data[field_name])
                if len(value) > pos:
                    return field_name
                pos -= len(value) + 1  # Account for space
        return "content"


# Global extractor instance
_extractor: EvidenceExtractor | None = None


def get_extractor() -> EvidenceExtractor:
    """Get the global evidence extractor."""
    global _extractor
    if _extractor is None:
        _extractor = EvidenceExtractor()
    return _extractor
