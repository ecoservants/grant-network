# backend/services/community-compute

# Community Compute Service

The Community Compute service is responsible for distributed, consent-aware processing of approved data jobs across registered community nodes.

It enforces policy, auditability, and safety by tracking jobs, execution status, and results in a structured and reviewable way.

## Database Schema

All database tables used by the Community Compute service are defined in the canonical schema file:

backend/db/schema.sql

diff
Copy code

This includes (but is not limited to):

- community_jobs
- community_job_results
- community_nodes
- community_node_sessions
- policy and allow-list tables

Do not define or duplicate schema files inside service directories.  
Do not recreate the legacy `dev/schema.sql` file from older Open Grant Network repositories.

## Purpose

Community Compute exists to:

- Distribute approved compute safely across community nodes
- Preserve consent and policy enforcement at every step
- Maintain full auditability of jobs and results
- Enable scale without centralizing risk
