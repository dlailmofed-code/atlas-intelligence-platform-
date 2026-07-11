"""
ATLAS Platform - Intelligence Engine

This package implements the core intelligence engine for ATLAS.

Components:
- Signals: Signal detection and aggregation
- Patterns: Pattern detection and analysis
- Causal: Causal reasoning and analysis
- Knowledge: Knowledge graph management
- Indicators: Intelligence indicators calculation
"""

from .base import (
    CausalRelationship,
    ConfidenceLevel,
    Evidence,
    EvidenceSource,
    Insight,
    IntelligenceSignal,
    OpportunityCandidate,
    Pattern,
    SignalCategory,
    SignalTrend,
    SignalType,
)
from .causal.reasoning import CausalGraph, CausalReasoner
from .engine import IntelligenceEngine, create_intelligence_engine
from .indicators.engine import IndicatorEngine, IndicatorTrendAnalyzer, IntelligenceIndicators
from .knowledge.graph import Entity, EntityType, KnowledgeGraph, Relationship
from .patterns.detector import InsightGenerator, PatternDetector
from .signals.detector import SignalAggregator, SignalDetector

__all__ = [
    "CausalGraph",
    # Causal components
    "CausalReasoner",
    "CausalRelationship",
    # Base types
    "ConfidenceLevel",
    # Knowledge graph components
    "Entity",
    "EntityType",
    "Evidence",
    "EvidenceSource",
    "IndicatorEngine",
    "IndicatorTrendAnalyzer",
    "Insight",
    "InsightGenerator",
    # Engine components
    "IntelligenceEngine",
    # Indicator components
    "IntelligenceIndicators",
    "IntelligenceSignal",
    "KnowledgeGraph",
    "OpportunityCandidate",
    "Pattern",
    # Pattern components
    "PatternDetector",
    "Relationship",
    "SignalAggregator",
    "SignalCategory",
    # Signal components
    "SignalDetector",
    "SignalTrend",
    "SignalType",
    "create_intelligence_engine",
]
