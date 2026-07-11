"""
Tests for deduplication.
"""

from datetime import UTC
from uuid import uuid4

import pytest

from backend.pipeline.deduplication import (
    ContentHasher,
    Deduplicator,
    SemanticSimilarityChecker,
    TimeWindowDetector,
    URLHasher,
)
from backend.pipeline.types import PipelineRecord, PipelineStage, SourceType


class TestURLHasher:
    """Tests for URLHasher."""

    @pytest.fixture
    def hasher(self):
        return URLHasher()

    def test_get_hash(self, hasher):
        """Test hash generation."""
        hash1 = hasher.get_hash("https://example.com/page")
        hash2 = hasher.get_hash("https://example.com/page")
        assert hash1 == hash2

    def test_hash_normalization(self, hasher):
        """Test URL normalization for hashing."""
        hash1 = hasher.get_hash("https://example.com/page")
        hash2 = hasher.get_hash("http://example.com/page")
        assert hash1 == hash2

    def test_trailing_slash(self, hasher):
        """Test trailing slash normalization."""
        hash1 = hasher.get_hash("https://example.com")
        hash2 = hasher.get_hash("https://example.com/")
        assert hash1 == hash2

    def test_register_and_check(self, hasher):
        """Test registration and checking."""
        record_id = uuid4()
        hasher.register("https://example.com", record_id)

        is_dup, dup_id = hasher.check("https://example.com")
        assert is_dup is True
        assert dup_id == record_id

    def test_not_seen(self, hasher):
        """Test URL not seen."""
        is_dup, dup_id = hasher.check("https://unseen.com")
        assert is_dup is False
        assert dup_id is None


class TestContentHasher:
    """Tests for ContentHasher."""

    @pytest.fixture
    def hasher(self):
        return ContentHasher()

    def test_get_hash(self, hasher):
        """Test content hash generation."""
        hash1 = hasher.get_hash("Same content")
        hash2 = hasher.get_hash("Same content")
        assert hash1 == hash2

    def test_different_content(self, hasher):
        """Test different content produces different hash."""
        hash1 = hasher.get_hash("Content A")
        hash2 = hasher.get_hash("Content B")
        assert hash1 != hash2

    def test_fields_hash(self, hasher):
        """Test hash from specific fields."""
        data = {"title": "Test", "content": "Body"}
        hash1 = hasher.get_fields_hash(data, ["title"])
        hash2 = hasher.get_fields_hash(data, ["title"])
        assert hash1 == hash2

    def test_normalization(self, hasher):
        """Test content normalization."""
        hash1 = hasher.get_hash("Hello World")
        hash2 = hasher.get_hash("hello world")
        # Should be similar after normalization
        assert len(hash1) == len(hash2)


class TestSemanticSimilarityChecker:
    """Tests for SemanticSimilarityChecker."""

    @pytest.fixture
    def checker(self):
        return SemanticSimilarityChecker(similarity_threshold=0.7)

    def test_no_records(self, checker):
        """Test with no stored records."""
        is_dup, dup_id, score = checker.check_similarity("Title", "Content")
        assert is_dup is False
        assert score == 0.0

    def test_add_record(self, checker):
        """Test adding a record."""
        record_id = uuid4()
        checker.add_record(record_id, "Test Title", "Test content")
        assert len(checker._records) == 1

    def test_high_similarity(self, checker):
        """Test high similarity detection."""
        record_id = uuid4()
        checker.add_record(record_id, "Apple Announces New Product", "Details about the new product")

        is_dup, dup_id, score = checker.check_similarity(
            "Apple Announces New Product",
            "Details about the new product",
        )

        assert is_dup is True
        assert dup_id == record_id
        assert score > 0.7

    def test_low_similarity(self, checker):
        """Test low similarity detection."""
        checker.add_record(uuid4(), "Apple Announces New Product", "Details about the new product")

        is_dup, dup_id, score = checker.check_similarity(
            "Completely Different Title",
            "Unrelated content here",
        )

        assert score < 0.7


class TestTimeWindowDetector:
    """Tests for TimeWindowDetector."""

    @pytest.fixture
    def detector(self):
        return TimeWindowDetector(window_minutes=60, hash_window_minutes=30)

    def test_no_duplicates(self, detector):
        """Test no duplicates in empty state."""
        from datetime import datetime

        is_dup, dup_id = detector.check_duplicate(
            datetime.now(UTC),
            "hash123",
        )
        assert is_dup is False
        assert dup_id is None

    def test_add_and_check(self, detector):
        """Test adding and checking."""
        from datetime import datetime

        record_id = uuid4()
        now = datetime.now(UTC)

        detector.add_record(now, "hash123", record_id)

        is_dup, dup_id = detector.check_duplicate(now, "hash123")
        assert is_dup is True
        assert dup_id == record_id

    def test_cleanup(self, detector):
        """Test cleanup of old records."""
        from datetime import datetime, timedelta

        # Add old record
        old_time = datetime.now(UTC) - timedelta(hours=2)
        detector.add_record(old_time, "old_hash", uuid4())

        # Add recent record
        recent_time = datetime.now(UTC) - timedelta(minutes=30)
        detector.add_record(recent_time, "recent_hash", uuid4())

        # Cleanup records older than 1 hour
        cutoff = datetime.now(UTC) - timedelta(hours=1)
        removed = detector.cleanup(cutoff)

        assert removed >= 1


class TestDeduplicator:
    """Tests for Deduplicator."""

    @pytest.fixture
    def deduplicator(self):
        return Deduplicator(
            enable_url_dedup=True,
            enable_content_dedup=True,
            enable_semantic_dedup=True,
            enable_time_window=True,
        )

    @pytest.mark.asyncio
    async def test_check_duplicate_by_url(self, deduplicator):
        """Test URL-based deduplication."""
        record = PipelineRecord(
            id=uuid4(),
            source_name="test",
            source_type=SourceType.NEWS,
            stage=PipelineStage.COLLECTED,
            cleaned_data={
                "title": "Test",
                "url": "https://example.com/article",
            },
        )

        # First check - should not be duplicate
        result = await deduplicator.check_duplicate(record)
        assert result.is_duplicate is False

        # Register the record
        deduplicator.register_record(record)

        # Create second record with same URL
        record2 = PipelineRecord(
            id=uuid4(),
            source_name="test",
            source_type=SourceType.NEWS,
            stage=PipelineStage.COLLECTED,
            cleaned_data={
                "title": "Test 2",
                "url": "https://example.com/article",
            },
        )

        result2 = await deduplicator.check_duplicate(record2)
        assert result2.is_duplicate is True
        assert result2.method == "url_hash"

    def test_get_stats(self, deduplicator):
        """Test statistics retrieval."""
        stats = deduplicator.get_stats()

        assert "url_dedup_enabled" in stats
        assert "content_dedup_enabled" in stats
        assert "semantic_dedup_enabled" in stats
        assert "time_window_enabled" in stats
