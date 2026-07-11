"""
ATLAS Platform - Data Collection Module

Handles data collection from connectors with orchestration, parallel collection, and batching.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from backend.connectors.base import ConnectorResponse
from backend.connectors.providers import get_connector
from backend.core.logging import get_logger
from backend.pipeline.types import PipelineRecord, SourceType

logger = get_logger(__name__)


@dataclass
class CollectionResult:
    """Result of a collection operation."""
    
    success: bool
    records: list[PipelineRecord] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    collection_time_ms: float = 0.0


@dataclass
class BatchConfig:
    """Configuration for batch collection."""
    
    batch_size: int = 100
    batch_delay_seconds: float = 0.5
    max_concurrent_batches: int = 5
    max_records_per_source: int = 1000


class ConnectorOrchestrator:
    """
    Orchestrates data collection from multiple connectors.
    
    Handles parallel collection, batching, and timeout management.
    """
    
    def __init__(
        self,
        batch_config: BatchConfig | None = None,
        default_timeout: int = 30,
    ):
        self.batch_config = batch_config or BatchConfig()
        self.default_timeout = default_timeout
        self._connectors: dict[str, Any] = {}
        self._collection_stats: dict[str, dict[str, Any]] = {}
    
    def _get_connector(self, source_name: str) -> Any:
        """Get or create a connector instance."""
        if source_name not in self._connectors:
            connector_class = get_connector(source_name)
            if connector_class:
                self._connectors[source_name] = connector_class()
            else:
                logger.warning(
                    "Connector not found",
                    extra={"source_name": source_name}
                )
        return self._connectors.get(source_name)
    
    async def collect(
        self,
        source_name: str,
        source_type: SourceType,
        params: dict[str, Any] | None = None,
        timeout: int | None = None,
    ) -> CollectionResult:
        """
        Collect data from a single source.
        
        Args:
            source_name: Name of the data source
            source_type: Type of the data source
            params: Collection parameters
            timeout: Request timeout in seconds
            
        Returns:
            CollectionResult with collected records
        """
        start_time = asyncio.get_event_loop().time()
        result = CollectionResult(success=False)
        
        connector = self._get_connector(source_name)
        if not connector:
            result.errors.append(f"Connector not found: {source_name}")
            return result
        
        params = params or {}
        timeout = timeout or self.default_timeout
        
        try:
            logger.info(
                "Starting collection",
                extra={
                    "source_name": source_name,
                    "params": params,
                }
            )
            
            # Call the connector's fetch method
            response = await asyncio.wait_for(
                connector.fetch(
                    endpoint=params.get("endpoint", ""),
                    params=params.get("query"),
                ),
                timeout=timeout,
            )
            
            if response.success:
                # Convert response to pipeline records
                records = self._create_records_from_response(
                    source_name=source_name,
                    source_type=source_type,
                    response=response,
                    metadata=params,
                )
                result.records = records
                result.success = True
                
                self._update_stats(source_name, success=True, record_count=len(records))
                
                logger.info(
                    "Collection completed",
                    extra={
                        "source_name": source_name,
                        "record_count": len(records),
                    }
                )
            else:
                result.errors.append(response.error_message or "Unknown error")
                self._update_stats(source_name, success=False, error=response.error_message)
        
        except asyncio.TimeoutError:
            error = f"Collection timeout after {timeout} seconds"
            result.errors.append(error)
            self._update_stats(source_name, success=False, error=error)
            logger.error(
                "Collection timeout",
                extra={"source_name": source_name, "timeout": timeout}
            )
        
        except Exception as e:
            error = f"Collection error: {str(e)}"
            result.errors.append(error)
            self._update_stats(source_name, success=False, error=error)
            logger.exception(
                "Collection error",
                extra={"source_name": source_name}
            )
        
        result.collection_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000
        return result
    
    async def collect_parallel(
        self,
        sources: list[tuple[str, SourceType, dict[str, Any]]],
        timeout: int | None = None,
    ) -> list[CollectionResult]:
        """
        Collect data from multiple sources in parallel.
        
        Args:
            sources: List of (source_name, source_type, params) tuples
            timeout: Timeout for each collection
            
        Returns:
            List of CollectionResult for each source
        """
        tasks = [
            self.collect(source_name, source_type, params, timeout)
            for source_name, source_type, params in sources
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    CollectionResult(
                        success=False,
                        errors=[str(result)],
                    )
                )
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def collect_with_batching(
        self,
        sources: list[tuple[str, SourceType, dict[str, Any]]],
    ) -> list[CollectionResult]:
        """
        Collect data from multiple sources with batching.
        
        Args:
            sources: List of (source_name, source_type, params) tuples
            
        Returns:
            List of CollectionResult for each source
        """
        all_results = []
        
        # Process in batches
        for i in range(0, len(sources), self.batch_config.max_concurrent_batches):
            batch = sources[i:i + self.batch_config.max_concurrent_batches]
            
            batch_results = await self.collect_parallel(batch)
            all_results.extend(batch_results)
            
            # Delay between batches
            if i + self.batch_config.max_concurrent_batches < len(sources):
                await asyncio.sleep(self.batch_config.batch_delay_seconds)
        
        return all_results
    
    def _create_records_from_response(
        self,
        source_name: str,
        source_type: SourceType,
        response: ConnectorResponse,
        metadata: dict[str, Any],
    ) -> list[PipelineRecord]:
        """Create pipeline records from a connector response."""
        records = []
        data = response.data
        
        if isinstance(data, dict):
            # Handle single record or dict response
            records.append(self._create_record(source_name, source_type, data, metadata))
        elif isinstance(data, list):
            # Handle list response
            for item in data[:self.batch_config.max_records_per_source]:
                if isinstance(item, dict):
                    records.append(
                        self._create_record(source_name, source_type, item, metadata)
                    )
        elif isinstance(data, str):
            # Handle text response
            records.append(
                self._create_record(
                    source_name,
                    source_type,
                    {"content": data},
                    metadata,
                )
            )
        
        return records
    
    def _create_record(
        self,
        source_name: str,
        source_type: SourceType,
        data: dict[str, Any],
        metadata: dict[str, Any],
    ) -> PipelineRecord:
        """Create a pipeline record from raw data."""
        return PipelineRecord(
            id=uuid4(),
            source_name=source_name,
            source_type=source_type,
            stage="collected",
            raw_data=data,
            metadata={
                "collection_metadata": metadata,
                "from_cache": data.get("_from_cache", False),
            },
        )
    
    def _update_stats(
        self,
        source_name: str,
        success: bool,
        record_count: int = 0,
        error: str | None = None,
    ) -> None:
        """Update collection statistics."""
        if source_name not in self._collection_stats:
            self._collection_stats[source_name] = {
                "total_collections": 0,
                "successful_collections": 0,
                "failed_collections": 0,
                "total_records": 0,
                "total_errors": 0,
                "errors": [],
            }
        
        stats = self._collection_stats[source_name]
        stats["total_collections"] += 1
        
        if success:
            stats["successful_collections"] += 1
            stats["total_records"] += record_count
        else:
            stats["failed_collections"] += 1
            stats["total_errors"] += 1
            if error:
                stats["errors"].append(error)
    
    def get_stats(self) -> dict[str, Any]:
        """Get collection statistics."""
        return {
            "connectors_initialized": len(self._connectors),
            "sources": self._collection_stats,
        }
    
    async def close(self) -> None:
        """Close all connector connections."""
        for name, connector in self._connectors.items():
            try:
                await connector.close()
            except Exception as e:
                logger.warning(
                    "Error closing connector",
                    extra={"source_name": name, "error": str(e)}
                )
        self._connectors.clear()


# Factory function for creating orchestrator
def create_orchestrator(
    batch_size: int = 100,
    batch_delay: float = 0.5,
    max_concurrent: int = 5,
    timeout: int = 30,
) -> ConnectorOrchestrator:
    """Create a configured ConnectorOrchestrator."""
    return ConnectorOrchestrator(
        batch_config=BatchConfig(
            batch_size=batch_size,
            batch_delay_seconds=batch_delay,
            max_concurrent_batches=max_concurrent,
        ),
        default_timeout=timeout,
    )
