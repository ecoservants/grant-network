# Open Grant Network Documentation

This directory contains the core planning and architecture documents for the Open Grant Network (OGN). It defines the system phases, the development roadmap, and the Community Compute specifications that power distributed ingestion.

---

## OGN Phases Overview

**Phase 0 – Foundation and Policy**  
Repository setup, allow-list policies, ethical crawling, initial schemas, and data governance rules.

**Phase 1 – Data Ingestion and Normalization**  
Core ingestion pipelines, IRS 990 parsing, Grants.gov ingestion, funder normalization, dedupe logic, and the first stable version of the unified grant schema.

**Phase 2 – Community Compute Infrastructure**  
Distributed job execution, node registration, verification, reputation systems, rate-limit compliance, and the compute job orchestration layer.

**Phase 3 – Advanced Intelligence Layer**  
Matching Engine v2, improved classification, geographic filters, clustering, confidence scoring, and quality signals.

**Phase 4 – UI, UX, Observability, and Release Prep**  
Public search UI, WordPress ESGT integration, analytics, testing, documentation, SDKs, and release hardening.

---

## Roadmap Files in This Directory

### `OGN_GitHub_Issues_00_250.md`  
This is the **canonical master roadmap** for the entire OGN project.  
It contains Issues 1–250 covering Phases 0 through 4.  
This file defines the official development sequence for all components including backend services, ingestion, matching, Community Compute, and the WordPress ESGT integration.

### `OGN_CC_Issues.md`  
This is the **Community Compute companion document**.  
It provides deep technical detail for CC-specific tasks referenced heavily in Phases 2 and 3, including distributed extraction, node verification, telemetry, consensus, and job orchestration.

Both documents work together.  
The master roadmap defines what must be built.  
The CC companion explains how distributed compute elements work and how they integrate with the main pipeline.

---

## How to Use These Documents

- Start with **OGN_GitHub_Issues_00_250.md** to understand the full lifecycle of the project.  
- Use **OGN_CC_Issues.md** when implementing or reviewing Community Compute modules, schemas, or infrastructure.  
- Treat both files as living documents kept in sync as the repository evolves.

---

## Related Directories

- `/docs/architecture/` – high-level diagrams, schemas, sequence flows  
- `/docs/tasks/` – implementation notes tied to specific issues  
- `/docs/workflows/` – ingestion flows, compute job execution, and API request lifecycles

---

If you add new phases, expand existing issues, or modify architectures, update this documentation first so the roadmap stays authoritative and clear.
