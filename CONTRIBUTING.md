# Contributing to the Grant Network

Thank you for your interest in contributing to the Grant Network. This project is part of the Open Grant Network (OGN) initiative and is built to prioritize clarity, safety, auditability, and long-term maintainability.

Please read this document carefully before making changes.

---

## General Expectations

- All contributors must work from the GitHub Issues and Project Boards
- Do not begin work unless the issue is assigned to you or explicitly approved
- Keep commits focused, descriptive, and aligned with the issue scope
- Ask questions early if requirements are unclear

This project favors correctness and clarity over speed.

---

## Branching & Commits

- Small changes may be committed directly to `main` if approved
- Larger or structural changes should be made in a feature branch and submitted via Pull Request
- Commit messages should clearly describe *what* changed and *why*

Example:


Add community_jobs and community_job_results tables


---

## Database Schema Rules (Important)

The Grant Network uses a **single source of truth** for database schema.

### Canonical Schema Location

All database tables must be defined in:



backend/db/schema.sql


A teardown/reset script is provided at:



backend/db/reset_schema.sql


### Rules

- ✅ All schema changes go in `backend/db/schema.sql`
- ❌ Do not create schema files inside service directories
- ❌ Do not recreate the legacy `dev/schema.sql` pattern
- ❌ Do not duplicate table definitions across files

If your issue requires new fields, indexes, or constraints, update the canonical schema file and reference the change in your commit or PR.

---

## Backend Services

Backend services live under:



backend/services/


Each service:
- Owns business logic and processing
- Does **not** own database schema
- May assume tables exist as defined in `backend/db/schema.sql`

Schema ownership is intentionally centralized.

---

## Community Compute Contributions

Community Compute is a core system responsible for distributed, consent-aware processing.

When contributing to Community Compute:
- Follow the existing schema and table naming conventions
- Ensure all actions are auditable and traceable
- Avoid hard-coded assumptions about nodes or execution context
- Keep safety and policy enforcement as first-class concerns

---

## Documentation

If you introduce or change behavior:
- Update the relevant README file
- Prefer clarity over verbosity
- Keep documentation close to the code it describes

---

## When in Doubt

If you are unsure about:
- Where code belongs
- Whether a schema change is appropriate
- How to interpret an issue requirement

**Pause and ask before proceeding.**

This helps protect the integrity of the system and saves time for everyone.

---

Thank you for contributing responsibly.CONTRIBUTING.md placeholder
