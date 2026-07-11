# Architecture Log

## Overview
This log tracks changes and updates to the ATLAS Platform architecture.

## Format
```
| Date | Change | Rationale | Impact | Architect |
|------|--------|----------|--------|-----------|
```

## Entries

### 2026-07-10 - Initial Architecture Design

| Field | Value |
|-------|-------|
| Change | Established multi-layered architecture with API, Services, Models, and Database layers |
| Rationale | Clean Architecture principles require clear separation between layers with dependencies pointing inward |
| Impact | Foundation for all future development |
| Architect | OpenHands Agent |

| Field | Value |
|-------|-------|
| Change | Implemented database models with soft delete support |
| Rationale | Soft delete preserves audit trail and allows recovery of accidentally deleted records |
| Impact | All core models now have deleted_at field for soft deletes |
| Architect | OpenHands Agent |

| Field | Value |
|-------|-------|
| Change | Created service layer for business logic encapsulation |
| Rationale | Services provide a clean interface between API endpoints and database operations |
| Impact | Business logic is now centralized and testable |
| Architect | OpenHands Agent |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
│                    (React/Next.js)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API Gateway Layer                            │
│                   (FastAPI - Router)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   Endpoints   │    │   Endpoints   │    │   Endpoints   │
│   (Health)    │    │   (Auth)      │    │   (Users)     │
└───────────────┘    └───────────────┘    └───────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ UserService │  │Opportunity  │  │Intelligence │              │
│  │             │  │  Service    │  │  Service    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Models Layer                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │  User   │  │Project  │  │Opport.  │  │ Signal  │            │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Database Layer                                │
│              PostgreSQL + SQLAlchemy Async                       │
└─────────────────────────────────────────────────────────────────┘
```
