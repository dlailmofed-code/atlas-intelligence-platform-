"""
ATLAS Platform - Pipeline Metrics Module

Tracks and reports pipeline performance metrics:
- Processing time
- Connector latency
- Queue length
- Throughput
- Failures
- Retry count
- Cache hit ratio
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from backend.core.logging import get_logger
from backend.pipeline.types import PipelineMetrics, PipelineStage

logger = get_logger(__name__)


@dataclass
class StageMetrics:
    """Metrics for a single pipeline stage."""

    name: PipelineStage
    total_processed: int = 0
    total_succeeded: int = 0
    total_failed: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float("inf")
    max_duration_ms: float = 0.0
    errors: dict[str, int] = field(default_factory=dict)

    @property
    def avg_duration_ms(self) -> float:
        if self.total_processed == 0:
            return 0.0
        return self.total_duration_ms / self.total_processed

    @property
    def success_rate(self) -> float:
        if self.total_processed == 0:
            return 0.0
        return self.total_succeeded / self.total_processed


@dataclass
class ConnectorMetrics:
    """Metrics for connector usage."""

    name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    min_latency_ms: float = float("inf")
    max_latency_ms: float = 0.0
    rate_limit_hits: int = 0

    @property
    def avg_latency_ms(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests


@dataclass
class JobMetrics:
    """Metrics for job execution."""

    total_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    retried_jobs: int = 0
    total_retries: int = 0
    total_duration_ms: float = 0.0

    @property
    def completion_rate(self) -> float:
        if self.total_jobs == 0:
            return 0.0
        return self.completed_jobs / self.total_jobs

    @property
    def avg_duration_ms(self) -> float:
        if self.completed_jobs == 0:
            return 0.0
        return self.total_duration_ms / self.completed_jobs


@dataclass
class CacheMetrics:
    """Metrics for cache performance."""

    hits: int = 0
    misses: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total


class MetricsCollector:
    """Collects and aggregates pipeline metrics."""

    def __init__(self):
        self._stage_metrics: dict[PipelineStage, StageMetrics] = {}
        self._connector_metrics: dict[str, ConnectorMetrics] = {}
        self._job_metrics = JobMetrics()
        self._cache_metrics = CacheMetrics()

        self._record_counts: dict[PipelineStage, int] = defaultdict(int)
        self._deduplication_count: int = 0
        self._evidence_count: int = 0
        self._start_time = time.time()

    def record_stage_start(self, stage: PipelineStage) -> float:
        """Record the start of a pipeline stage."""
        if stage not in self._stage_metrics:
            self._stage_metrics[stage] = StageMetrics(name=stage)
        return time.time()

    def record_stage_end(
        self,
        stage: PipelineStage,
        start_time: float,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """Record the end of a pipeline stage."""
        duration_ms = (time.time() - start_time) * 1000

        metrics = self._stage_metrics.get(stage)
        if metrics:
            metrics.total_processed += 1
            metrics.total_duration_ms += duration_ms
            metrics.min_duration_ms = min(metrics.min_duration_ms, duration_ms)
            metrics.max_duration_ms = max(metrics.max_duration_ms, duration_ms)

            if success:
                metrics.total_succeeded += 1
            else:
                metrics.total_failed += 1
                if error:
                    metrics.errors[error] = metrics.errors.get(error, 0) + 1

    def record_connector_request(
        self,
        connector_name: str,
        latency_ms: float,
        success: bool = True,
        rate_limited: bool = False,
    ) -> None:
        """Record a connector request."""
        if connector_name not in self._connector_metrics:
            self._connector_metrics[connector_name] = ConnectorMetrics(name=connector_name)

        metrics = self._connector_metrics[connector_name]
        metrics.total_requests += 1

        if success:
            metrics.successful_requests += 1
            metrics.total_latency_ms += latency_ms
            metrics.min_latency_ms = min(metrics.min_latency_ms, latency_ms)
            metrics.max_latency_ms = max(metrics.max_latency_ms, latency_ms)
        else:
            metrics.failed_requests += 1

        if rate_limited:
            metrics.rate_limit_hits += 1

    def record_job(
        self,
        completed: bool = True,
        failed: bool = False,
        retried: bool = False,
        duration_ms: float = 0.0,
    ) -> None:
        """Record job execution."""
        self._job_metrics.total_jobs += 1

        if completed:
            self._job_metrics.completed_jobs += 1
            self._job_metrics.total_duration_ms += duration_ms
        elif failed:
            self._job_metrics.failed_jobs += 1

        if retried:
            self._job_metrics.retried_jobs += 1
            self._job_metrics.total_retries += 1

    def record_cache_hit(self, hit: bool) -> None:
        """Record cache hit or miss."""
        if hit:
            self._cache_metrics.hits += 1
        else:
            self._cache_metrics.misses += 1

    def record_deduplication(self) -> None:
        """Record a deduplicated record."""
        self._deduplication_count += 1

    def record_evidence_extraction(self, count: int = 1) -> None:
        """Record evidence extraction."""
        self._evidence_count += count

    def record_record_count(self, stage: PipelineStage, count: int = 1) -> None:
        """Record number of records at a stage."""
        self._record_counts[stage] += count

    def get_pipeline_metrics(self) -> PipelineMetrics:
        """Get aggregated pipeline metrics."""
        total_processing_time = sum(
            m.total_duration_ms for m in self._stage_metrics.values()
        )

        return PipelineMetrics(
            jobs_total=self._job_metrics.total_jobs,
            jobs_completed=self._job_metrics.completed_jobs,
            jobs_failed=self._job_metrics.failed_jobs,
            jobs_retried=self._job_metrics.total_retries,
            records_processed=sum(self._record_counts.values()),
            records_deduplicated=self._deduplication_count,
            evidence_extracted=self._evidence_count,
            total_processing_time_ms=total_processing_time,
            avg_processing_time_ms=(
                total_processing_time / sum(m.total_processed for m in self._stage_metrics.values())
                if self._record_counts.get(PipelineStage.STORED, 0) > 0
                else 0.0
            ),
            connector_latencies={
                name: [m.min_latency_ms, m.avg_latency_ms, m.max_latency_ms]
                for name, m in self._connector_metrics.items()
            },
            cache_hits=self._cache_metrics.hits,
            cache_misses=self._cache_metrics.misses,
            stage_durations_ms={
                stage: m.avg_duration_ms
                for stage, m in self._stage_metrics.items()
            },
            last_updated=datetime.now(UTC),
        )

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of all metrics."""
        uptime_seconds = time.time() - self._start_time

        return {
            "uptime_seconds": uptime_seconds,
            "jobs": {
                "total": self._job_metrics.total_jobs,
                "completed": self._job_metrics.completed_jobs,
                "failed": self._job_metrics.failed_jobs,
                "retried": self._job_metrics.total_retries,
                "completion_rate": f"{self._job_metrics.completion_rate:.2%}",
                "avg_duration_ms": f"{self._job_metrics.avg_duration_ms:.2f}",
            },
            "records": {
                "total_processed": sum(self._record_counts.values()),
                "deduplicated": self._deduplication_count,
                "evidence_extracted": self._evidence_count,
            },
            "stages": {
                stage.value: {
                    "processed": m.total_processed,
                    "succeeded": m.total_succeeded,
                    "failed": m.total_failed,
                    "success_rate": f"{m.success_rate:.2%}",
                    "avg_duration_ms": f"{m.avg_duration_ms:.2f}",
                }
                for stage, m in self._stage_metrics.items()
            },
            "connectors": {
                name: {
                    "requests": m.total_requests,
                    "success_rate": f"{m.success_rate:.2%}",
                    "avg_latency_ms": f"{m.avg_latency_ms:.2f}",
                    "rate_limit_hits": m.rate_limit_hits,
                }
                for name, m in self._connector_metrics.items()
            },
            "cache": {
                "hits": self._cache_metrics.hits,
                "misses": self._cache_metrics.misses,
                "hit_rate": f"{self._cache_metrics.hit_rate:.2%}",
            },
        }

    def get_detailed_stage_metrics(self) -> dict[str, StageMetrics]:
        """Get detailed stage metrics."""
        return dict(self._stage_metrics)

    def get_connector_metrics(self) -> dict[str, ConnectorMetrics]:
        """Get connector metrics."""
        return dict(self._connector_metrics)

    def reset(self) -> None:
        """Reset all metrics."""
        self._stage_metrics.clear()
        self._connector_metrics.clear()
        self._job_metrics = JobMetrics()
        self._cache_metrics = CacheMetrics()
        self._record_counts.clear()
        self._deduplication_count = 0
        self._evidence_count = 0
        self._start_time = time.time()

        logger.info("Metrics reset")


class MetricsReporter:
    """Reports metrics in various formats."""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector

    def to_json(self) -> dict[str, Any]:
        """Export metrics as JSON."""
        return self.metrics.get_summary()

    def to_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        summary = self.metrics.get_summary()

        # Job metrics
        lines.append("# HELP atlas_jobs_total Total number of jobs")
        lines.append("# TYPE atlas_jobs_total counter")
        lines.append(f'atlas_jobs_total{{status="total"}} {summary["jobs"]["total"]}')
        lines.append(f'atlas_jobs_total{{status="completed"}} {summary["jobs"]["completed"]}')
        lines.append(f'atlas_jobs_total{{status="failed"}} {summary["jobs"]["failed"]}')

        # Record metrics
        lines.append("# HELP atlas_records_total Total records processed")
        lines.append("# TYPE atlas_records_total counter")
        lines.append(f'atlas_records_total {summary["records"]["total_processed"]}')
        lines.append(f'atlas_records_deduplicated_total {summary["records"]["deduplicated"]}')
        lines.append(f'atlas_evidence_extracted_total {summary["records"]["evidence_extracted"]}')

        # Cache metrics
        lines.append("# HELP atlas_cache_hits_total Cache hits")
        lines.append("# TYPE atlas_cache_hits_total counter")
        lines.append(f'atlas_cache_hits_total {summary["cache"]["hits"]}')
        lines.append(f'atlas_cache_misses_total {summary["cache"]["misses"]}')

        return "\n".join(lines)

    def to_datadog(self) -> list[dict[str, Any]]:
        """Export metrics in Datadog format."""
        metrics = []
        summary = self.metrics.get_summary()

        # Job metrics
        metrics.extend([
            {
                "metric": "atlas.jobs.total",
                "points": [(int(time.time()), summary["jobs"]["total"])],
                "type": "count",
            },
            {
                "metric": "atlas.jobs.completed",
                "points": [(int(time.time()), summary["jobs"]["completed"])],
                "type": "count",
            },
            {
                "metric": "atlas.jobs.failed",
                "points": [(int(time.time()), summary["jobs"]["failed"])],
                "type": "count",
            },
        ])

        # Cache metrics
        metrics.extend([
            {
                "metric": "atlas.cache.hits",
                "points": [(int(time.time()), summary["cache"]["hits"])],
                "type": "count",
            },
            {
                "metric": "atlas.cache.misses",
                "points": [(int(time.time()), summary["cache"]["misses"])],
                "type": "count",
            },
        ])

        return metrics


# Global metrics collector instance
_metrics_collector: MetricsCollector | None = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_metrics_reporter() -> MetricsReporter:
    """Get the global metrics reporter."""
    return MetricsReporter(get_metrics_collector())
