# Backend Services

This directory contains the core backend services that power the Grant Network.

Each service is responsible for a specific domain of functionality but **does not own database schema definitions**.

## Database Schema

All database tables used by backend services are defined in the canonical schema file:

backend/db/schema.sql

pgsql
Copy code

Service directories must not define or duplicate SQL schema files.

## Services

- `community-compute/`  
  Distributed, consent-aware compute system for executing approved data jobs across registered community nodes.  
  Tracks jobs, execution state, results, and audit metadata.

- `crawler/`  
  Crawling and ingestion services operating under allow-list, robots, and policy constraints.

Additional services may be added here as the Grant Network expands.

## Design Principles

- Single source of truth for database schema
- Clear separation between services and persistence
- Auditability, policy enforcement, and safety by default
- No legacy `dev/schema.sql` usage
