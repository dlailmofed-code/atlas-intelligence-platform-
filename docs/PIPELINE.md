# ATLAS Platform - Data Pipeline

## Overview

The ATLAS Platform Data Pipeline provides end-to-end processing of data from various connectors, including validation, cleaning, normalization, deduplication, evidence extraction, and knowledge graph integration.

## Architecture

```
backend/pipeline/
├── __init__.py           # Module exports
├── types.py              # Type definitions
├── engine.py             # Main pipeline orchestration
├── scheduler/            # Job scheduling and queue management
├── collection/           # Data collection from connectors
├── validation/           # Data validation
├── cleaning/            # Data cleaning
├── normalization/        # Data normalization
├── deduplication/       # Record deduplication
├── extraction/          # Evidence extraction
├── graph/              # Knowledge graph management
├── metrics/            # Pipeline metrics
└── storage/            # Data storage
```

## Pipeline Stages

The pipeline processes records through the following stages:

1. **RAW** - Raw data from connectors
2. **COLLECTED** - Data collected from sources
3. **VALIDATED** - Schema and source validation
4. **CLEANED** - HTML removal, whitespace normalization
5. **NORMALIZED** - Date, currency, country normalization
6. **DEDUPLICATED** - Duplicate detection
7. **EXTRACTED** - Evidence extraction
8. **ENRICHED** - Knowledge graph updates
9. **STORED** - Persisted to storage

## Modules

### 1. Scheduler (`scheduler/`)

Handles job scheduling, priority queue, retries, and failure recovery.

**Components:**
- `PriorityQueue` - Thread-safe priority queue
- `JobRetryManager` - Exponential backoff retry logic
- `FailureRecoveryManager` - Dead letter queue management
- `Scheduler` - Main scheduler with worker pool

**Features:**
- Priority-based job processing
- Automatic retry with backoff
- Dead letter queue for failed jobs
- Scheduled recurring jobs

### 2. Data Collection (`collection/`)

Collects data from connectors with orchestration.

**Components:**
- `ConnectorOrchestrator` - Multi-connector orchestration
- `BatchConfig` - Batch processing configuration

**Features:**
- Parallel collection from multiple sources
- Batch processing
- Timeout management
- Collection statistics

### 3. Validation (`validation/`)

Validates data against schemas and sources.

**Components:**
- `SchemaValidator` - Schema-based validation
- `SourceValidator` - Source authenticity validation
- `MalformedRecordDetector` - Spam and malformed content detection

**Features:**
- Schema definitions for different source types
- Confidence scoring
- Required field validation
- Pattern validation

### 4. Cleaning (`cleaning/`)

Cleans and normalizes text data.

**Components:**
- `HTMLCleaner` - HTML tag and entity removal
- `WhitespaceNormalizer` - Whitespace normalization
- `UnicodeNormalizer` - Unicode normalization
- `EncodingCleaner` - Control character removal
- `LanguageCleaner` - Language-specific cleaning

**Features:**
- HTML removal
- Unicode normalization
- Control character removal
- URL/email/phone removal
- Language-specific fixes

### 5. Normalization (`normalization/`)

Normalizes structured data fields.

**Components:**
- `DateNormalizer` - Date format normalization
- `CurrencyNormalizer` - Currency value parsing
- `CountryNormalizer` - Country name/code normalization
- `LanguageNormalizer` - Language normalization
- `CompanyNormalizer` - Company name normalization
- `PersonNormalizer` - Person name normalization
- `LocationNormalizer` - Location parsing

**Features:**
- ISO date formatting
- Currency parsing and formatting
- Country name standardization
- Language code mapping
- Name normalization

### 6. Deduplication (`deduplication/`)

Detects duplicate records.

**Components:**
- `URLHasher` - URL-based deduplication
- `ContentHasher` - Content hash deduplication
- `SemanticSimilarityChecker` - Semantic similarity detection
- `TimeWindowDetector` - Time-window duplicate detection
- `Deduplicator` - Main deduplication coordinator

**Features:**
- URL hash matching
- Content hash matching
- Semantic similarity (n-gram based)
- Time-window duplicate detection
- Configurable thresholds

### 7. Evidence Extraction (`extraction/`)

Extracts entities and evidence from records.

**Components:**
- `EntityExtractor` - Entity extraction from text
- `ValueExtractor` - Financial values and dates
- `EvidenceExtractor` - Main extraction coordinator

**Extracts:**
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

### 8. Knowledge Graph (`graph/`)

Manages the knowledge graph.

**Components:**
- `EntityManager` - Entity CRUD operations
- `RelationshipManager` - Relationship management
- `EvidenceLinker` - Evidence linking
- `KnowledgeGraph` - Main graph coordinator

**Features:**
- Entity creation and updates
- Relationship inference
- Evidence linking
- Confidence scoring

### 9. Metrics (`metrics/`)

Collects and reports pipeline metrics.

**Components:**
- `MetricsCollector` - Metrics collection
- `MetricsReporter` - Metrics export

**Tracks:**
- Processing time
- Connector latency
- Queue length
- Throughput
- Failures
- Retry count
- Cache hit ratio

### 10. Storage (`storage/`)

Persists pipeline data.

**Components:**
- `InMemoryStorage` - In-memory storage
- `StorageManager` - Storage operations

**Stores:**
- Raw data
- Normalized data
- Validated data
- Evidence
- Knowledge graph data

## Usage

### Basic Pipeline Usage

```python
from backend.pipeline.engine import get_pipeline_engine
from backend.pipeline.types import SourceType

# Get pipeline engine
engine = get_pipeline_engine()

# Collect and process data
records = await engine.collect_and_process(
    source_name="newsapi",
    source_type=SourceType.NEWS,
    params={"query": "AI startups"},
)

# Get pipeline stats
stats = engine.get_stats()
```

### Processing Individual Records

```python
from backend.pipeline.types import PipelineRecord, SourceType, PipelineStage
from uuid import uuid4

# Create a record
record = PipelineRecord(
    id=uuid4(),
    source_name="test",
    source_type=SourceType.WEB,
    stage=PipelineStage.RAW,
    raw_data={"title": "Test", "content": "Content"},
)

# Process through pipeline
processed = await engine.process_record(record)
```

### Using the Scheduler

```python
from backend.pipeline.scheduler import get_scheduler, JobPriority

scheduler = get_scheduler()

# Submit a job
job = await scheduler.submit(
    job_type="collect",
    source_name="newsapi",
    source_type="news",
    params={"query": "AI"},
    priority=JobPriority.HIGH,
)

# Start workers
await scheduler.start_workers(num_workers=5)
```

### Deduplication

```python
from backend.pipeline.deduplication import get_deduplicator

deduplicator = get_deduplicator()

# Check for duplicates
result = await deduplicator.check_duplicate(record)

if result.is_duplicate:
    print(f"Duplicate of {result.duplicate_id}")
else:
    # Register for future deduplication
    deduplicator.register_record(record)
```

### Evidence Extraction

```python
from backend.pipeline.extraction import get_extractor

extractor = get_extractor()

# Extract evidence
evidence = extractor.extract_evidence(record)

for e in evidence:
    print(f"{e.entity_type}: {e.entity_name} ({e.confidence})")
```

### Knowledge Graph

```python
from backend.pipeline.graph import get_knowledge_graph

graph = get_knowledge_graph()

# Update from evidence
stats = graph.update_from_evidence(record, evidence)

print(f"Created {stats['entities_created']} entities")
print(f"Created {stats['relationships_created']} relationships")
```

### Metrics

```python
from backend.pipeline.metrics import get_metrics_collector, get_metrics_reporter

collector = get_metrics_collector()
reporter = get_metrics_reporter()

# Get JSON metrics
json_metrics = reporter.to_json()

# Get Prometheus format
prometheus_metrics = reporter.to_prometheus()
```

## Configuration

Configure the pipeline via environment variables:

```bash
# Pipeline Settings
PIPELINE_MAX_PARALLEL_JOBS=10
PIPELINE_JOB_TIMEOUT_SECONDS=300
PIPELINE_BATCH_SIZE=100
PIPELINE_ENABLE_DEDUPLICATION=true
PIPELINE_ENABLE_EVIDENCE_EXTRACTION=true
PIPELINE_CONFIDENCE_THRESHOLD=0.7

# Retry Settings
PIPELINE_RETRY_MAX_ATTEMPTS=3
PIPELINE_RETRY_BACKOFF_SECONDS=60

# Deduplication Settings
DEDUP_SEMANTIC_THRESHOLD=0.85
```

## Testing

Run pipeline tests:

```bash
cd backend
pytest tests/unit/test_pipeline/ -v
```

## Error Handling

The pipeline implements comprehensive error handling:

1. **Validation Errors** - Records with validation errors are flagged
2. **Processing Errors** - Errors are recorded per stage
3. **Retry Logic** - Failed jobs are retried with exponential backoff
4. **Dead Letter Queue** - Jobs that exceed retry limits go to DLQ
5. **Graceful Degradation** - Pipeline continues even if individual stages fail

## Performance

- **Parallel Processing** - Multiple records processed concurrently
- **Batching** - Efficient batch processing for collections
- **Caching** - In-memory caching for deduplication
- **Async I/O** - All operations are async-compatible

## Extending the Pipeline

### Adding a New Stage

1. Add the stage to `PipelineStage` enum in `types.py`
2. Implement the stage method in `PipelineEngine`
3. Add metrics tracking
4. Add storage support if needed

### Adding a New Extractor

1. Implement extractor in `extraction/`
2. Register with `EvidenceExtractor`
3. Add tests
4. Update documentation

### Adding a New Deduplication Strategy

1. Implement deduplication method in `deduplication/`
2. Register with `Deduplicator`
3. Add configuration option
4. Add tests
