"""
ATLAS Platform - Pipeline Scheduler

Handles job scheduling, priority queue, retries, and failure recovery.
"""

import asyncio
import heapq
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Coroutine, TypeVar
from uuid import UUID, uuid4

from backend.core.logging import get_logger
from backend.pipeline.types import JobPriority, JobStatus, PipelineJob

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class ScheduledJob:
    """A scheduled recurring job."""
    
    id: UUID
    name: str
    func_name: str
    interval_seconds: int
    enabled: bool = True
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None
    max_consecutive_failures: int = 3
    consecutive_failures: int = 0


class PriorityQueue:
    """
    Thread-safe priority queue for pipeline jobs.
    
    Higher priority jobs are processed first.
    Jobs with the same priority are processed in FIFO order.
    """
    
    def __init__(self):
        self._heap: list[tuple[int, float, PipelineJob]] = []
        self._entry_finder: dict[UUID, tuple[int, float, PipelineJob]] = {}
        self._counter = 0
        self._lock = asyncio.Lock()
    
    async def put(self, job: PipelineJob) -> None:
        """Add a job to the queue."""
        async with self._lock:
            entry = (-job.priority.value, self._counter, job)
            self._entry_finder[job.id] = entry
            heapq.heappush(self._heap, entry)
            self._counter += 1
            logger.debug(
                "Job added to queue",
                extra={"job_id": str(job.id), "priority": job.priority.value}
            )
    
    async def get(self) -> PipelineJob | None:
        """Get the highest priority job from the queue."""
        async with self._lock:
            while self._heap:
                priority, counter, job = heapq.heappop(self._heap)
                if job.id in self._entry_finder:
                    del self._entry_finder[job.id]
                    job.status = JobStatus.QUEUED
                    logger.debug(
                        "Job retrieved from queue",
                        extra={"job_id": str(job.id), "priority": job.priority.value}
                    )
                    return job
            return None
    
    async def remove(self, job_id: UUID) -> bool:
        """Remove a job from the queue."""
        async with self._lock:
            if job_id in self._entry_finder:
                del self._entry_finder[job_id]
                return True
            return False
    
    async def reprioritize(self, job_id: UUID, new_priority: JobPriority) -> bool:
        """Change the priority of a job in the queue."""
        async with self._lock:
            if job_id not in self._entry_finder:
                return False
            
            # Remove old entry
            old_priority, counter, job = self._entry_finder[job_id]
            del self._entry_finder[job_id]
            
            # Find and remove from heap
            for i, (p, c, j) in enumerate(self._heap):
                if j.id == job_id:
                    self._heap.pop(i)
                    heapq.heapify(self._heap)
                    break
            
            # Add with new priority
            job.priority = new_priority
            entry = (-new_priority.value, self._counter, job)
            self._entry_finder[job.id] = entry
            heapq.heappush(self._heap, entry)
            self._counter += 1
            
            logger.debug(
                "Job priority changed",
                extra={"job_id": str(job.id), "new_priority": new_priority.value}
            )
            return True
    
    async def size(self) -> int:
        """Get the number of jobs in the queue."""
        async with self._lock:
            return len(self._heap)
    
    async def clear(self) -> None:
        """Clear all jobs from the queue."""
        async with self._lock:
            self._heap.clear()
            self._entry_finder.clear()


class JobRetryManager:
    """Manages job retries with exponential backoff."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_backoff_seconds: int = 60,
        max_backoff_seconds: int = 3600,
    ):
        self.max_retries = max_retries
        self.base_backoff_seconds = base_backoff_seconds
        self.max_backoff_seconds = max_backoff_seconds
        self._retry_counts: dict[UUID, int] = defaultdict(int)
        self._last_retry_at: dict[UUID, datetime] = {}
    
    def can_retry(self, job: PipelineJob) -> bool:
        """Check if a job can be retried."""
        return job.retry_count < job.max_retries and job.retry_count < self.max_retries
    
    def get_backoff_seconds(self, job: PipelineJob) -> int:
        """Calculate backoff time for a job retry."""
        backoff = self.base_backoff_seconds * (2 ** job.retry_count)
        return min(backoff, self.max_backoff_seconds)
    
    def should_retry_now(self, job: PipelineJob) -> bool:
        """Check if a job should be retried now based on backoff."""
        if job.id not in self._last_retry_at:
            return True
        
        last_retry = self._last_retry_at[job.id]
        backoff = self.get_backoff_seconds(job)
        return datetime.now(timezone.utc) >= last_retry + timedelta(seconds=backoff)
    
    def record_retry(self, job: PipelineJob) -> None:
        """Record a job retry attempt."""
        job.retry_count += 1
        job.status = JobStatus.RETRYING
        self._retry_counts[job.id] = job.retry_count
        self._last_retry_at[job.id] = datetime.now(timezone.utc)
        
        logger.info(
            "Job retry recorded",
            extra={
                "job_id": str(job.id),
                "retry_count": job.retry_count,
                "backoff_seconds": self.get_backoff_seconds(job),
            }
        )
    
    def reset_retry(self, job_id: UUID) -> None:
        """Reset retry state for a job."""
        if job_id in self._retry_counts:
            del self._retry_counts[job_id]
        if job_id in self._last_retry_at:
            del self._last_retry_at[job_id]
    
    def get_retry_count(self, job_id: UUID) -> int:
        """Get the retry count for a job."""
        return self._retry_counts.get(job_id, 0)


class FailureRecoveryManager:
    """Manages job failure recovery and dead letter queue."""
    
    def __init__(
        self,
        max_failures_before_dlq: int = 5,
        dlq_retention_days: int = 30,
    ):
        self.max_failures_before_dlq = max_failures_before_dlq
        self.dlq_retention_days = dlq_retention_days
        self._dead_letter_queue: dict[UUID, PipelineJob] = {}
        self._failure_counts: dict[UUID, int] = defaultdict(int)
        self._failure_reasons: dict[UUID, list[str]] = defaultdict(list)
    
    def record_failure(self, job: PipelineJob, error: str) -> None:
        """Record a job failure."""
        self._failure_counts[job.id] += 1
        self._failure_reasons[job.id].append(error)
        
        if self._failure_counts[job.id] >= self.max_failures_before_dlq:
            job.status = JobStatus.FAILED
            self._dead_letter_queue[job.id] = job
            logger.warning(
                "Job moved to dead letter queue",
                extra={
                    "job_id": str(job.id),
                    "failure_count": self._failure_counts[job.id],
                }
            )
    
    def get_failure_count(self, job_id: UUID) -> int:
        """Get the failure count for a job."""
        return self._failure_counts.get(job_id, 0)
    
    def get_dead_letter_jobs(self) -> list[PipelineJob]:
        """Get all jobs in the dead letter queue."""
        return list(self._dead_letter_queue.values())
    
    def get_failure_reasons(self, job_id: UUID) -> list[str]:
        """Get failure reasons for a job."""
        return self._failure_reasons.get(job_id, [])
    
    def remove_from_dlq(self, job_id: UUID) -> bool:
        """Remove a job from the dead letter queue."""
        if job_id in self._dead_letter_queue:
            del self._dead_letter_queue[job_id]
            del self._failure_counts[job_id]
            del self._failure_reasons[job_id]
            return True
        return False
    
    def retry_from_dlq(self, job_id: UUID) -> PipelineJob | None:
        """Reset a job for retry from dead letter queue."""
        if job_id in self._dead_letter_queue:
            job = self._dead_letter_queue[job_id]
            job.status = JobStatus.PENDING
            job.retry_count = 0
            del self._failure_counts[job_id]
            del self._failure_reasons[job_id]
            del self._dead_letter_queue[job_id]
            return job
        return None


class Scheduler:
    """
    Main scheduler for pipeline jobs.
    
    Handles job scheduling, execution, retries, and failure recovery.
    """
    
    def __init__(
        self,
        config: dict[str, Any] | None = None,
    ):
        self.config = config or {}
        self._queue = PriorityQueue()
        self._retry_manager = JobRetryManager(
            max_retries=self.config.get("max_retries", 3),
            base_backoff_seconds=self.config.get("retry_backoff_seconds", 60),
            max_backoff_seconds=self.config.get("max_backoff_seconds", 3600),
        )
        self._failure_manager = FailureRecoveryManager(
            max_failures_before_dlq=self.config.get("max_failures_before_dlq", 5),
        )
        self._running = False
        self._workers: list[asyncio.Task] = []
        self._scheduled_jobs: dict[str, ScheduledJob] = {}
        self._job_handlers: dict[str, Callable[..., Coroutine[Any, Any, Any]]] = {}
        self._stats = {
            "jobs_submitted": 0,
            "jobs_completed": 0,
            "jobs_failed": 0,
            "jobs_retried": 0,
        }
        self._lock = asyncio.Lock()
    
    @property
    def queue(self) -> PriorityQueue:
        """Get the job queue."""
        return self._queue
    
    @property
    def stats(self) -> dict[str, Any]:
        """Get scheduler statistics."""
        return {
            **self._stats,
            "queue_size": self._queue.size(),
            "dead_letter_size": len(self._failure_manager.get_dead_letter_jobs()),
            "scheduled_jobs": len(self._scheduled_jobs),
        }
    
    def register_handler(
        self,
        job_type: str,
        handler: Callable[..., Coroutine[Any, Any, Any]],
    ) -> None:
        """Register a job handler function."""
        self._job_handlers[job_type] = handler
        logger.info(
            "Job handler registered",
            extra={"job_type": job_type}
        )
    
    def register_scheduled_job(
        self,
        name: str,
        func_name: str,
        interval_seconds: int,
        enabled: bool = True,
    ) -> ScheduledJob:
        """Register a recurring scheduled job."""
        job = ScheduledJob(
            id=uuid4(),
            name=name,
            func_name=func_name,
            interval_seconds=interval_seconds,
            enabled=enabled,
        )
        self._scheduled_jobs[name] = job
        logger.info(
            "Scheduled job registered",
            extra={"name": name, "interval_seconds": interval_seconds}
        )
        return job
    
    async def submit(
        self,
        job_type: str,
        source_name: str,
        source_type: str,
        params: dict[str, Any] | None = None,
        priority: JobPriority = JobPriority.NORMAL,
        max_retries: int = 3,
    ) -> PipelineJob:
        """Submit a new job to the scheduler."""
        job = PipelineJob(
            id=uuid4(),
            job_type=job_type,
            source_name=source_name,
            source_type=source_type,
            priority=priority,
            params=params or {},
            max_retries=max_retries,
        )
        
        await self._queue.put(job)
        self._stats["jobs_submitted"] += 1
        
        logger.info(
            "Job submitted",
            extra={
                "job_id": str(job.id),
                "job_type": job_type,
                "source_name": source_name,
                "priority": priority.value,
            }
        )
        
        return job
    
    async def submit_batch(
        self,
        jobs: list[dict[str, Any]],
    ) -> list[PipelineJob]:
        """Submit multiple jobs in batch."""
        submitted = []
        for job_spec in jobs:
            job = await self.submit(
                job_type=job_spec["job_type"],
                source_name=job_spec["source_name"],
                source_type=job_spec["source_type"],
                params=job_spec.get("params"),
                priority=JobSpec.get("priority", JobPriority.NORMAL),
            )
            submitted.append(job)
        
        logger.info(
            "Batch jobs submitted",
            extra={"count": len(submitted)}
        )
        
        return submitted
    
    async def process_job(self, job: PipelineJob) -> PipelineJob:
        """Process a single job."""
        job.started_at = datetime.now(timezone.utc)
        job.status = JobStatus.RUNNING
        
        logger.info(
            "Job started",
            extra={
                "job_id": str(job.id),
                "job_type": job.job_type,
            }
        )
        
        handler = self._job_handlers.get(job.job_type)
        if not handler:
            job.status = JobStatus.FAILED
            job.error_message = f"No handler registered for job type: {job.job_type}"
            self._failure_manager.record_failure(job, job.error_message)
            return job
        
        try:
            job.result = await handler(job)
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            self._stats["jobs_completed"] += 1
            self._retry_manager.reset_retry(job.id)
            
            logger.info(
                "Job completed",
                extra={
                    "job_id": str(job.id),
                    "duration_ms": (
                        job.completed_at - job.started_at
                    ).total_seconds() * 1000 if job.completed_at and job.started_at else 0,
                }
            )
        
        except Exception as e:
            job.error_message = str(e)
            
            if self._retry_manager.can_retry(job):
                self._retry_manager.record_retry(job)
                self._stats["jobs_retried"] += 1
                
                # Re-queue for retry
                await self._queue.put(job)
            else:
                job.status = JobStatus.FAILED
                self._failure_manager.record_failure(job, str(e))
                self._stats["jobs_failed"] += 1
                
                logger.error(
                    "Job failed",
                    extra={
                        "job_id": str(job.id),
                        "error": str(e),
                        "retry_count": job.retry_count,
                    }
                )
        
        return job
    
    async def start_workers(self, num_workers: int = 5) -> None:
        """Start worker tasks to process jobs."""
        self._running = True
        
        for i in range(num_workers):
            task = asyncio.create_task(self._worker(i))
            self._workers.append(task)
        
        logger.info(
            "Scheduler workers started",
            extra={"num_workers": num_workers}
        )
    
    async def stop_workers(self) -> None:
        """Stop all worker tasks."""
        self._running = False
        
        for task in self._workers:
            task.cancel()
        
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        
        logger.info("Scheduler workers stopped")
    
    async def _worker(self, worker_id: int) -> None:
        """Worker task that processes jobs from the queue."""
        logger.debug(
            "Worker started",
            extra={"worker_id": worker_id}
        )
        
        while self._running:
            try:
                job = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=1.0,
                )
                
                if job:
                    # Check if job should be retried (backoff)
                    if job.status == JobStatus.RETRYING:
                        if not self._retry_manager.should_retry_now(job):
                            # Put back in queue
                            await self._queue.put(job)
                            await asyncio.sleep(1)
                            continue
                    
                    await self.process_job(job)
            
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.exception(
                    "Worker error",
                    extra={"worker_id": worker_id, "error": str(e)}
                )
                await asyncio.sleep(1)
    
    async def get_queue_stats(self) -> dict[str, Any]:
        """Get queue statistics."""
        return {
            "size": await self._queue.size(),
            "dead_letter_size": len(self._failure_manager.get_dead_letter_jobs()),
            "retry_pending": sum(
                1 for _ in self._failure_manager.get_dead_letter_jobs()
                if _.status == JobStatus.RETRYING
            ),
        }


# Global scheduler instance
_scheduler: Scheduler | None = None


def get_scheduler() -> Scheduler:
    """Get the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler()
    return _scheduler
