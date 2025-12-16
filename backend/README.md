# Backend

This directory contains the backend services, utilities, and database schema for the Grant Network.

## Database Schema

The canonical database schema for the Grant Network lives in:

backend/db/schema.sql

kotlin
Copy code

All database tables for Community Compute and related backend services must be defined in this file.

A companion teardown script is available at:

backend/db/reset_schema.sql

markdown
Copy code

Do not recreate or use the legacy `dev/schema.sql` pattern from earlier Open Grant Network repositories.

## Structure

- `api/` – API routes and handlers
- `db/` – Canonical database schema and reset scripts
- `services/` – Backend services (including Community Compute)
- `utils/` – Shared backend utilities
