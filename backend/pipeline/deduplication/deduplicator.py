"""
ATLAS Platform - Data Deduplication Module

Handles record deduplication using multiple strategies:
- URL hash
- Content hash
- Semantic similarity
- Time-window duplicate detection
"""

import hashlib
import re
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from backend.core.logging import get_logger
from backend.pipeline.types import DeduplicationResult, PipelineRecord

logger = get_logger(__name__)


class URLHasher:
    """Generates hashes for URL-based deduplication."""

    def __init__(self):
        self._seen_urls: dict[str, UUID] = {}

    def get_hash(self, url: str) -> str:
        """Generate a normalized hash for a URL."""
        if not url:
            return ""

        # Normalize URL
        normalized = self._normalize_url(url)

        # Generate hash
        return hashlib.sha256(normalized.encode()).hexdigest()[:32]

    def _normalize_url(self, url: str) -> str:
        """Normalize a URL for consistent hashing."""
        # Strip protocol
        url = re.sub(r"^https?://", "", url.lower())

        # Remove trailing slash
        url = url.rstrip("/")

        # Remove www prefix
        url = re.sub(r"^www\.", "", url)

        # Remove query parameters (optional)
        # url = url.split("?")[0]

        # Remove fragments
        url = url.split("#")[0]

        return url

    def register(self, url: str, record_id: UUID) -> None:
        """Register a URL with its record ID."""
        hash_value = self.get_hash(url)
        if hash_value:
            self._seen_urls[hash_value] = record_id

    def check(self, url: str) -> tuple[bool, UUID | None]:
        """Check if a URL has been seen."""
        hash_value = self.get_hash(url)
        if hash_value in self._seen_urls:
            return True, self._seen_urls[hash_value]
        return False, None

    def clear(self) -> None:
        """Clear all registered URLs."""
        self._seen_urls.clear()


class ContentHasher:
    """Generates hashes for content-based deduplication."""

    def __init__(self):
        self._seen_hashes: dict[str, UUID] = {}

    def get_hash(
        self,
        content: str,
        fields: list[str] | None = None,
    ) -> str:
        """Generate a hash for content."""
        if not content:
            return ""

        # Normalize content
        normalized = self._normalize_content(content)

        # Generate hash
        return hashlib.sha256(normalized.encode()).hexdigest()[:32]

    def get_fields_hash(
        self,
        data: dict[str, Any],
        fields: list[str],
    ) -> str:
        """Generate a hash from specific fields in data."""
        field_values = []

        for field in fields:
            value = data.get(field)
            if value:
                if isinstance(value, str):
                    field_values.append(value.lower().strip())
                else:
                    field_values.append(str(value))

        content = "|".join(field_values)
        return self.get_hash(content)

    def _normalize_content(self, content: str) -> str:
        """Normalize content for consistent hashing."""
        # Convert to lowercase
        content = content.lower()

        # Remove URLs
        content = re.sub(r"https?://\S+", "", content)

        # Remove extra whitespace
        content = re.sub(r"\s+", " ", content)

        # Remove punctuation
        content = re.sub(r"[^\w\s]", "", content)

        return content.strip()

    def register(self, content: str, record_id: UUID) -> None:
        """Register content with its record ID."""
        hash_value = self.get_hash(content)
        if hash_value:
            self._seen_hashes[hash_value] = record_id

    def check(self, content: str) -> tuple[bool, UUID | None]:
        """Check if content has been seen."""
        hash_value = self.get_hash(content)
        if hash_value in self._seen_hashes:
            return True, self._seen_hashes[hash_value]
        return False, None

    def clear(self) -> None:
        """Clear all registered content hashes."""
        self._seen_hashes.clear()


class SemanticSimilarityChecker:
    """Checks for semantic similarity between records."""

    def __init__(
        self,
        similarity_threshold: float = 0.85,
        use_ngrams: bool = True,
        ngram_size: int = 3,
    ):
        self.similarity_threshold = similarity_threshold
        self.use_ngrams = use_ngrams
        self.ngram_size = ngram_size
        self._records: list[dict[str, Any]] = []

    def add_record(self, record_id: UUID, title: str, content: str) -> None:
        """Add a record for similarity comparison."""
        self._records.append({
            "id": record_id,
            "title": title,
            "content": content,
            "combined": f"{title} {content}".lower(),
        })

    def check_similarity(
        self,
        title: str,
        content: str,
    ) -> tuple[bool, UUID | None, float]:
        """
        Check if a record is similar to any existing records.
        
        Returns:
            Tuple of (is_duplicate, duplicate_id, similarity_score)
        """
        if not self._records:
            return False, None, 0.0

        combined = f"{title} {content}".lower()

        max_similarity = 0.0
        most_similar_id = None

        for record in self._records:
            similarity = self._calculate_similarity(
                combined,
                record["combined"],
            )

            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_id = record["id"]

        if max_similarity >= self.similarity_threshold:
            return True, most_similar_id, max_similarity

        return False, None, max_similarity

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        if self.use_ngrams:
            return self._ngram_similarity(text1, text2)
        return self._jaccard_similarity(text1, text2)

    def _ngram_similarity(self, text1: str, text2: str) -> float:
        """Calculate n-gram similarity."""
        ngrams1 = self._get_ngrams(text1)
        ngrams2 = self._get_ngrams(text2)

        if not ngrams1 or not ngrams2:
            return 0.0

        intersection = len(ngrams1 & ngrams2)
        union = len(ngrams1 | ngrams2)

        if union == 0:
            return 0.0

        return intersection / union

    def _get_ngrams(self, text: str) -> set[str]:
        """Get character n-grams from text."""
        text = re.sub(r"[^\w\s]", "", text.lower())
        words = text.split()

        ngrams = set()
        for word in words:
            if len(word) >= self.ngram_size:
                for i in range(len(word) - self.ngram_size + 1):
                    ngrams.add(word[i:i + self.ngram_size])

        return ngrams

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity."""
        words1 = set(re.sub(r"[^\w\s]", "", text1.lower()).split())
        words2 = set(re.sub(r"[^\w\s]", "", text2.lower()).split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        if union == 0:
            return 0.0

        return intersection / union

    def clear(self) -> None:
        """Clear all stored records."""
        self._records.clear()


class TimeWindowDetector:
    """Detects duplicates within a time window."""

    def __init__(
        self,
        window_minutes: int = 60,
        hash_window_minutes: int = 30,
    ):
        self.window_minutes = window_minutes
        self.hash_window_minutes = hash_window_minutes
        self._records_by_time: list[tuple[datetime, str, UUID]] = []

    def add_record(
        self,
        timestamp: datetime,
        content_hash: str,
        record_id: UUID,
    ) -> None:
        """Add a record to the time window."""
        self._records_by_time.append((timestamp, content_hash, record_id))

    def check_duplicate(
        self,
        timestamp: datetime,
        content_hash: str,
    ) -> tuple[bool, UUID | None]:
        """
        Check for duplicates within the time window.
        
        Returns:
            Tuple of (is_duplicate, duplicate_id)
        """
        window_start = timestamp - timedelta(minutes=self.window_minutes)
        hash_window_start = timestamp - timedelta(minutes=self.hash_window_minutes)

        for record_time, record_hash, record_id in reversed(self._records_by_time):
            # Check if within time window
            if record_time < window_start:
                break

            # Check exact hash match within hash window
            if record_time >= hash_window_start:
                if record_hash == content_hash:
                    return True, record_id

            # Check similar content within full window
            # (This is a simplified check - could use similarity)

        return False, None

    def cleanup(self, before: datetime) -> int:
        """Remove records older than specified time."""
        original_count = len(self._records_by_time)
        self._records_by_time = [
            (t, h, r) for t, h, r in self._records_by_time
            if t >= before
        ]
        return original_count - len(self._records_by_time)


class Deduplicator:
    """
    Main deduplicator that coordinates all deduplication strategies.
    """

    def __init__(
        self,
        enable_url_dedup: bool = True,
        enable_content_dedup: bool = True,
        enable_semantic_dedup: bool = True,
        enable_time_window: bool = True,
        semantic_threshold: float = 0.85,
    ):
        self.enable_url_dedup = enable_url_dedup
        self.enable_content_dedup = enable_content_dedup
        self.enable_semantic_dedup = enable_semantic_dedup
        self.enable_time_window = enable_time_window

        # Initialize detectors
        self._url_hasher = URLHasher()
        self._content_hasher = ContentHasher()
        self._semantic_checker = SemanticSimilarityChecker(
            similarity_threshold=semantic_threshold,
        )
        self._time_window = TimeWindowDetector()

    async def check_duplicate(
        self,
        record: PipelineRecord,
    ) -> DeduplicationResult:
        """
        Check if a record is a duplicate.
        
        Args:
            record: The record to check
            
        Returns:
            DeduplicationResult with duplicate status
        """
        data = record.cleaned_data or record.normalized_data or {}

        # Check URL-based deduplication
        if self.enable_url_dedup:
            url = data.get("url")
            if url:
                is_dup, dup_id = self._url_hasher.check(url)
                if is_dup:
                    return DeduplicationResult(
                        is_duplicate=True,
                        duplicate_id=dup_id,
                        method="url_hash",
                        similarity_score=1.0,
                    )

        # Check content-based deduplication
        if self.enable_content_dedup:
            title = data.get("title", "")
            content = data.get("content", "") or data.get("description", "")

            if title and content:
                content_hash = self._content_hasher.get_fields_hash(
                    data, ["title", "content"]
                )
                is_dup, dup_id = self._content_hasher.check(
                    f"{title} {content}"
                )
                if is_dup:
                    return DeduplicationResult(
                        is_duplicate=True,
                        duplicate_id=dup_id,
                        method="content_hash",
                        similarity_score=1.0,
                    )

        # Check semantic similarity
        if self.enable_semantic_dedup:
            title = data.get("title", "")
            content = data.get("content", "") or data.get("description", "")

            if title and content:
                is_dup, dup_id, similarity = self._semantic_checker.check_similarity(
                    title, content
                )
                if is_dup:
                    return DeduplicationResult(
                        is_duplicate=True,
                        duplicate_id=dup_id,
                        method="semantic_similarity",
                        similarity_score=similarity,
                    )

        # Check time window
        if self.enable_time_window:
            content_hash = self._content_hasher.get_fields_hash(
                data, ["title"]
            )
            timestamp = record.created_at

            is_dup, dup_id = self._time_window.check_duplicate(
                timestamp, content_hash
            )
            if is_dup:
                return DeduplicationResult(
                    is_duplicate=True,
                    duplicate_id=dup_id,
                    method="time_window",
                    similarity_score=1.0,
                )

        return DeduplicationResult(
            is_duplicate=False,
            method="none",
            similarity_score=0.0,
        )

    def register_record(self, record: PipelineRecord) -> None:
        """Register a record after processing."""
        data = record.cleaned_data or record.normalized_data or {}

        # Register URL
        url = data.get("url")
        if url:
            self._url_hasher.register(url, record.id)

        # Register content
        title = data.get("title", "")
        content = data.get("content", "") or data.get("description", "")

        if title:
            content_hash = self._content_hasher.get_fields_hash(
                data, ["title", "content"]
            )
            self._content_hasher.register(f"{title} {content}", record.id)

            # Register for semantic comparison
            self._semantic_checker.add_record(record.id, title, content)

            # Register for time window
            self._time_window.add_record(
                record.created_at,
                content_hash,
                record.id,
            )

    def get_stats(self) -> dict[str, Any]:
        """Get deduplication statistics."""
        return {
            "url_dedup_enabled": self.enable_url_dedup,
            "content_dedup_enabled": self.enable_content_dedup,
            "semantic_dedup_enabled": self.enable_semantic_dedup,
            "time_window_enabled": self.enable_time_window,
            "records_in_semantic_index": len(self._semantic_checker._records),
            "records_in_time_window": len(self._time_window._records_by_time),
        }

    def clear(self) -> None:
        """Clear all deduplication state."""
        self._url_hasher.clear()
        self._content_hasher.clear()
        self._semantic_checker.clear()
        self._records_by_time = []


# Global deduplicator instance
_deduplicator: Deduplicator | None = None


def get_deduplicator() -> Deduplicator:
    """Get the global deduplicator."""
    global _deduplicator
    if _deduplicator is None:
        _deduplicator = Deduplicator()
    return _deduplicator
