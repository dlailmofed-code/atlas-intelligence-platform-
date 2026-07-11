"""
ATLAS Platform - Knowledge Graph Module
"""

from backend.pipeline.graph.knowledge_graph import (
    EntityManager,
    EvidenceLinker,
    GraphEntity,
    KnowledgeGraph,
    RelationshipManager,
    get_knowledge_graph,
)

__all__ = [
    "KnowledgeGraph",
    "EntityManager",
    "RelationshipManager",
    "EvidenceLinker",
    "GraphEntity",
    "get_knowledge_graph",
]
