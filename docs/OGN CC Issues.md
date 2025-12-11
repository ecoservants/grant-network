## Community Compute

CC-01 — Create community_nodes table

Community Compute Tasks

## Summary
Create the `community_nodes` table which stores the identity, consent, and authentication details for each compute node participating in the Grant Network.

## Requirements
- Add `community_nodes` to `dev/schema.sql`
- Include fields: node_public_id, api_token, consent_hash, consent_version, user_id, timestamps, is_active
- Ensure compatibility with existing tables
- Follow naming conventions used in the schema

## Deliverables
- Updated `dev/schema.sql` with new table definition
- Migration notes
- Documentation block in schema file

## Acceptance Criteria
- Table builds without errors
- Fields match the documented Community Compute plan
- External keys (if used) reference valid IDs
- Schema integrates cleanly with future endpoints

## Suggested Labels
community-compute, database, schema, phase-2

CC-02 — Create community_node_sessions table

Community Compute Tasks

## Summary
Create the `community_node_sessions` table to track active and historical sessions for compute nodes.

## Requirements
- Extend `dev/schema.sql` and add a new table
- Include: session_token, node_id, created_at, last_seen_at, user_agent, ip_hash, is_active
- Add foreign key linking back to `community_nodes`

## Deliverables
- Updated schema with session table
- Foreign key relationship with community_nodes
- Documentation for field purposes

## Acceptance Criteria
- Table builds successfully with FK constraint
- Session lookup queries work using node_id
- Schema reviewed and approved by maintainers

## Suggested Labels
community-compute, database, authentication, schema, phase-2

CC-03 — Create community_jobs table

Community Compute Tasks

## Summary
Create the `community_jobs` table, which stores jobs to be assigned to distributed compute nodes.

## Requirements
- Add community_jobs table to schema
- Fields: job_type, payload_json, status, timestamps
- Include claimed_by_node_id and FK to community_nodes

## Deliverables
- Updated dev/schema.sql with table definition
- Indexes for job status and job_type
- Notes for scheduler integration

## Acceptance Criteria
- Table builds successfully
- Able to insert pending jobs and update statuses
- FK constraints validated

## Suggested Labels
community-compute, database, scheduling, schema, phase-2

CC-04 — Create community_job_results table

Community Compute Tasks

## Summary
Create the `community_job_results` table to store the results submitted by compute nodes after completing distributed tasks.

## Requirements
- Add table with fields: job_id, node_id, result_json, result_checksum, timestamps
- Add FK references to community_jobs and community_nodes
- Ensure schema supports checksum validation

## Deliverables
- Updated schema with job results table
- Foreign key definitions and indexes
- Basic documentation for API use

## Acceptance Criteria
- Table builds without errors
- Results correctly link to jobs and nodes
- Checksum field supports integrity verification

## Suggested Labels
community-compute, database, job-processing, schema, phase-2

CC-05 — Convert allow-list CSV into SQL schema

Community Compute Tasks

## Summary
Convert the existing allow-list CSV and robots audit summary into a proper SQL table structure to support job generation and policy enforcement.

## Requirements
- Design one or more tables replacing Allow_List_Policy_v1.csv and robots_audit_summary.csv
- Add definitions to `dev/schema.sql`
- Ensure orchestrators can query allowed domains directly
- Consider indexing by domain and permission rules

## Deliverables
- New SQL tables for allow-list and robots audit data
- Migration/loader notes
- Documentation describing schema and table relationships

## Acceptance Criteria
- CSV data can be fully migrated into new tables
- Schema supports efficient queries for job creation
- All allow-list and robots fields preserved

## Suggested Labels
community-compute, database, policy, crawler, schema, phase-2


CC-10 — Implement /compute/register-node endpoint
## Summary
Implement the `/compute/register-node` endpoint used when a compute node first joins the network. This endpoint issues a Node Public ID and API token, creates a node record, and initializes session handling.

## Requirements
- Accept basic metadata: user_agent, consent_flag, optional user_id
- Generate Node Public ID (uuid4) and secure API token
- Store node record in community_nodes table
- Create initial session in community_node_sessions
- Return node_public_id, session_token, and server time

## Deliverables
- New FastAPI route: POST /compute/register-node
- Registration service module
- Validation + error handling
- Unit tests for registration flow

## Acceptance Criteria
- New nodes can register and receive credentials
- Session is created automatically upon registration
- Duplicate registrations handled safely
- Endpoint documented in API reference

## Suggested Labels
api, community-compute, authentication, backend, phase-2

CC-11 — Implement /compute/consent endpoint
## Summary
Implement the `/compute/consent` endpoint that securely records user consent for participation in Community Compute and stores the consent version hash.

## Requirements
- Validate node API token
- Accept consent_version and consent_hash
- Update community_nodes with consent values
- Log consent event for auditing
- Support both new consent and updated consent

## Deliverables
- POST /compute/consent route
- Consent handler service
- Audit event entry in community_nodes or separate audit log
- Test cases for invalid/expired tokens

## Acceptance Criteria
- Consent is recorded and persists across sessions
- Missing or invalid tokens return proper 401/403 responses
- Consent updates overwrite previous versions safely
- Documentation explains consent lifecycle

## Suggested Labels
api, compliance, community-compute, authentication, phase-2

CC-12 — Implement /compute/opt-out endpoint
## Summary
Implement the `/compute/opt-out` endpoint allowing any node to revoke participation, invalidate tokens, terminate sessions, and remove itself from job assignment eligibility.

## Requirements
- Validate node identity via API token
- Mark node as inactive (is_active = false)
- Terminate all active sessions in community_node_sessions
- Revoke outstanding jobs by reassigning or marking abandoned
- Log opt-out event

## Deliverables
- POST /compute/opt-out endpoint
- Node deactivation flow
- Session invalidation logic
- Job cancellation or reassignment policy implementation

## Acceptance Criteria
- Opt-out fully disables node participation
- Sessions cannot continue after deactivation
- Outstanding tasks handled safely without orphaning
- Node appears inactive in admin view

## Suggested Labels
api, community-compute, compliance, backend, phase-2

CC-13 — Implement /compute/job endpoint (Job Fetcher)
## Summary
Implement the `/compute/job` endpoint that assigns a pending job to a compute node, respecting rate limits, consent requirements, and job-type rules.

## Requirements
- Validate node authorization + active status
- Require valid consent before returning jobs
- Implement scheduling logic:
  - Fetch next unclaimed job
  - Mark job as claimed_by_node_id
  - Set claim timestamp
- Prevent over-assignment, rapid polling, and duplicate claims

## Deliverables
- GET /compute/job endpoint
- Job scheduling module
- Node eligibility checks (IP hash, throttle, consent)
- Unit tests for job assignment behavior

## Acceptance Criteria
- Node receives at most one uncompleted job at a time
- Jobs transition from "pending" → "claimed"
- Ineligible nodes receive correct error codes
- Scheduler handles concurrency correctly

## Suggested Labels
api, scheduling, community-compute, backend, phase-2

CC-14 — Implement /compute/job/result endpoint (Job Result Submission)
## Summary
Implement the endpoint used by compute nodes to submit results for assigned jobs. Supports JSON results, checksums, and job-status transitions.

## Requirements
- Validate API token + claimed job ownership
- Accept result_json and result_checksum
- Verify integrity of submitted data
- Update community_job_results and mark job as completed
- Trigger follow-up orchestration events (indexing, merging, validation)

## Deliverables
- POST /compute/job/result endpoint
- Result validation module
- Job-status update logic
- Test cases for invalid ownership, checksum mismatch

## Acceptance Criteria
- Only the node that claimed the job may submit results
- Completed jobs are stored with checksum integrity
- Bad submissions rejected with descriptive errors
- Results appear correctly in admin/monitoring views

## Suggested Labels
api, job-processing, community-compute, backend, phase-2

CC-15 — Implement rate limiting for compute endpoints
## Summary
Implement adaptive rate limiting across all Community Compute endpoints to protect the API from runaway nodes, botnets, or misconfigured clients.

## Requirements
- Apply per-node, per-endpoint, and global rate limits
- Exponential backoff for nodes polling too frequently
- Integrate with community_node_sessions to track last_seen
- Provide descriptive 429 responses with retry-after headers
- Log rate-limit violations for investigation

## Deliverables
- Rate limit middleware for compute routes
- Node polling throttling logic
- Configuration file for rate thresholds
- Documentation explaining expected fetch intervals

## Acceptance Criteria
- Misbehaving nodes receive controlled throttles
- Normal nodes do not experience unintended blocking
- Logs clearly show rate-limit events
- Rate-limit rules adjustable without code changes

## Suggested Labels
security, performance, community-compute, api, backend, phase-2

CC-20 — Implement Node Telemetry Capture (heartbeat + system info)
## Summary
Implement telemetry collection so compute nodes periodically send heartbeat signals and optional system metadata to maintain accurate status, health checks, and scheduling eligibility.

## Requirements
- Add POST /compute/telemetry endpoint
- Fields: session_token, cpu_load, memory_free, last_job_ms, network_latency_ms
- Store heartbeat in community_node_sessions.last_seen_at
- Record metadata in a new telemetry table or JSON column
- Implement soft warnings for unstable nodes

## Deliverables
- Telemetry endpoint
- Telemetry storage mechanism
- Update scheduler to check last_seen_at freshness
- Unit tests for heartbeat interval violations

## Acceptance Criteria
- Nodes missing N heartbeats become temporarily ineligible
- Telemetry recorded with no performance degradation
- Scheduler uses telemetry for job assignment decisions
- Documentation includes recommended heartbeat frequency

## Suggested Labels
community-compute, backend, monitoring, api, phase-2

CC-21 — Implement Node Health Status Classification
## Summary
Add a health scoring system that classifies nodes as healthy, unstable, offline, or banned based on telemetry, job success rates, and policy violations.

## Requirements
- Define health states: healthy, unstable, offline, banned
- Implement scoring inputs:
  - Telemetry staleness
  - Job success/failure rates
  - Rate-limit violations
  - Consent or policy violations
- Store health state in community_nodes table
- Integrate health checks into scheduler

## Deliverables
- Health classification service module
- Cron or background task to recalc health scores
- Scheduler updates to exclude unstable/offline nodes

## Acceptance Criteria
- Health states update automatically based on rules
- Unstable nodes receive fewer jobs or throttles
- Offline nodes cannot receive new tasks
- Banned nodes blocked entirely with 403 errors

## Suggested Labels
community-compute, reliability, backend, scheduler, phase-2

CC-22 — Implement Orchestrator Logs (Job Lifecycle Logging)
## Summary
Implement a unified logging system for the Community Compute orchestrator, capturing job lifecycle events, node decisions, failures, retries, and reassignment.

## Requirements
- Create orchestrator_log table or structured log format
- Log key events:
  - job_created
  - job_claimed
  - job_result_submitted
  - job_reassigned
  - job_failed
  - node_rate_limited
- Add correlation IDs to group events
- Expose admin-only logs endpoint or database view

## Deliverables
- Orchestrator logging module
- Log table or file-based system
- Documentation of log event schema

## Acceptance Criteria
- Every job transitions recorded with timestamps
- Logs support triage and debugging with correlation IDs
- Admins can review orchestrator behavior
- Supports future analytics on job throughput and node reliability

## Suggested Labels
community-compute, logging, monitoring, backend, phase-2

CC-23 — Implement Node Reputation Score (trust + reliability index)
## Summary
Establish a reputation scoring system for compute nodes based on job accuracy, consistency, latency, and compliance, enabling better scheduling and fraud detection.

## Requirements
- Inputs for scoring:
  - job success rate
  - result checksum consistency
  - average job completion latency
  - telemetry stability
  - historical violations
- Store reputation_score (0–100) in community_nodes
- Adjust scheduler to prioritize high-reputation nodes

## Deliverables
- Reputation scoring module
- Reputation recalculation task
- Scheduler integration
- Unit tests for scoring scenarios

## Acceptance Criteria
- High-reputation nodes receive larger workloads
- Low-reputation nodes throttled or limited
- Reputation changes based on real node performance
- Reputation score visible in admin dashboards

## Suggested Labels
community-compute, security, scheduler, reliability, phase-2

CC-24 — Implement Fairness Scheduler (distribution balancing)
## Summary
Add fairness mechanisms to ensure job distribution is balanced across nodes, preventing starvation or dominance by fast/high-capacity nodes.

## Requirements
- Implement round-robin or weighted fairness algorithm
- Consider:
  - node health
  - reputation
  - recent workload volume
- Introduce a “cooldown” period to avoid hogging
- Ensure fairness does not reduce performance significantly

## Deliverables
- FairnessScheduler class or module
- Integration with /compute/job assignment flow
- New fields: recent_jobs_count, last_assignment_at

## Acceptance Criteria
- No single node repeatedly claims jobs disproportionately
- Low but healthy nodes receive a fair share of tasks
- Scheduler balances fairness with throughput efficiency
- Admin logs confirm even distribution over time

## Suggested Labels
community-compute, scheduler, performance, backend, phase-2

CC-25 — Implement Scheduler Backoff Logic (progressive delays for unstable nodes)
## Summary
Add backoff logic so unstable or frequently failing nodes receive progressively longer delays before becoming eligible for new jobs.

## Requirements
- Backoff stages: mild → moderate → severe → suspended
- Triggers:
  - repeated job failures
  - repeated rate-limit hits
  - telemetry instability
- Cooldown timer stored per node in community_nodes
- Scheduler must honor backoff rules

## Deliverables
- Backoff engine module
- Fields in community_nodes: backoff_until, backoff_level
- Update job assignment logic to respect cooldown periods

## Acceptance Criteria
- Unstable nodes receive fewer jobs automatically
- Backoff resets gradually after good performance
- Repeated violations escalate backoff stage
- Logs clearly show when backoff is applied

## Suggested Labels
community-compute, scheduler, reliability, backend, phase-2

CC-30 — Implement Job Retry Policy (requeue failed or expired jobs)
## Summary
Implement a robust retry system for jobs that fail, timeout, or produce invalid results. Jobs must be requeued safely without duplication, ensuring compute continuity.

## Requirements
- Add retry fields to community_jobs:
  - retry_count
  - last_retry_at
  - max_retries
- Conditions for retry:
  - node failure
  - checksum mismatch
  - invalid output format
  - telemetry instability during job execution
- Ensure idempotent retry logic
- Prevent infinite retry loops

## Deliverables
- RetryPolicy module
- Scheduler integration for pending → retryable jobs
- Logging for retry events
- Unit tests for all retry paths

## Acceptance Criteria
- Jobs retry automatically when conditions met
- Retries capped by max_retries policy
- No duplicate claims of the same job
- Logs clearly record all retry events

## Suggested Labels
community-compute, scheduler, reliability, backend, phase-2

CC-31 — Implement Abandonment Detection (claimed-but-never-finished jobs)
## Summary
Implement abandonment detection to find jobs that were claimed by a node but never completed due to disconnects, crashes, or node instability.

## Requirements
- Add abandonment rules:
  - If no result within X minutes → abandoned
  - If node heartbeat missing → abandoned
  - If node enters backoff → abandoned
- Mark jobs abandoned and eligible for reassignment
- Increment node failure counters

## Deliverables
- AbandonmentDetector module
- Background task or cron job
- SQL updates for job abandonment status

## Acceptance Criteria
- Abandoned jobs become pending or retryable
- Nodes with repeated abandonments lose reputation
- Abandonment events appear in orchestrator logs
- No abandoned job becomes permanently stuck

## Suggested Labels
community-compute, scheduler, monitoring, reliability, phase-2

CC-32 — Implement Job Cleanup Routine (completed / failed / expired)
## Summary
Implement periodic cleanup of finished, expired, or permanently failed jobs to keep the Community Compute DB healthy and performant.

## Requirements
- Implement cleanup categories:
  - completed jobs
  - max-retry-exceeded jobs
  - expired jobs (based on TTL)
- Delete or archive results into cold storage tables
- Provide configurable retention period

## Deliverables
- CleanupService module
- Cron or background scheduler triggers
- Archival storage table or S3/minio bucket (JSON)

## Acceptance Criteria
- Old records moved or deleted safely
- No job data lost before retention threshold
- System performance improved after cleanup
- Cleanup operations logged for audits

## Suggested Labels
community-compute, maintenance, backend, performance, phase-2

CC-33 — Implement Multi-Node Result Validation (consensus engine)
## Summary
Implement a consensus-based validation mechanism that assigns certain jobs to multiple nodes and compares results to ensure correctness and detect malicious behavior.

## Requirements
- Support job types requiring multi-node verification
- Compare result_json payloads across nodes
- Define matching thresholds (exact, fuzzy, semantic)
- Penalize nodes that repeatedly disagree with consensus
- Promote verified results to “finalized” status

## Deliverables
- ValidationEngine module
- Consensus comparison functions
- Job-status transitions (partial → verified → finalized)

## Acceptance Criteria
- Multi-node jobs only finalize after consistent agreement
- Disagreeing nodes lose reputation
- Consensus rules configurable per job type
- Logs show validation details clearly

## Suggested Labels
community-compute, security, job-processing, backend, phase-2

CC-34 — Implement Result Merge + Review Workflow
## Summary
Implement a post-processing workflow that merges community compute outputs into canonical datasets, with optional human review for critical changes.

## Requirements
- Support merge rules:
  - append
  - overwrite
  - merge by primary key
- Produce diffs for human review when required
- Track merge events and reviewer approvals
- Update downstream indexes after merge

## Deliverables
- MergeEngine module
- Reviewer queue UI (admin-only)
- Versioned dataset storage (v1, v2, etc.)

## Acceptance Criteria
- Results merged correctly with no data corruption
- Reviewer sees clear diffs for manual approval
- Dataset version increments automatically
- Merge events logged with correlation IDs

## Suggested Labels
community-compute, data-pipeline, job-processing, backend, phase-2

CC-35 — Implement Final Validation Pipeline (before publishing outputs)
## Summary
Build an automated validation pipeline that performs structural checks, schema compliance, checksum validation, and business-rule enforcement before any result is accepted.

## Requirements
- Validate result_json against official schemas
- Check for:
  - missing mandatory fields
  - invalid formats
  - forbidden values
  - checksum mismatches
- Reject or quarantine invalid results
- Pipeline trigger integrates with merge engine

## Deliverables
- ValidationPipeline module
- JSON Schema definitions
- Quarantine job table for invalid artifacts

## Acceptance Criteria
- Invalid results never reach final datasets
- Failed validations produce descriptive error logs
- Schema changes are version-controlled
- Pipeline must pass in CI before deployment

## Suggested Labels
community-compute, validation, security, backend, phase-2

CC-40 — Implement Job Batching Engine (split large datasets into batches)
## Summary
Create a batching engine that converts large datasets (IRS 990, Grants.gov, foundation directories) into smaller job units for distributed processing across compute nodes.

## Requirements
- Accept dataset ingestion input (files, API responses, database records)
- Split records into consistent batch sizes (configurable)
- Create community_jobs entries for each batch
- Maintain ordering, batch_id, dataset_version fields
- Support rebalancing when batches fail

## Deliverables
- BatchingEngine module
- Batch metadata schema updates
- Admin function to create batches per dataset

## Acceptance Criteria
- Large datasets split predictably into evenly sized batches
- Failed batches requeued with no duplication
- Orchestrator can generate 100s–1000s of jobs efficiently
- Batches traceable back to dataset source and version

## Suggested Labels
community-compute, data-pipeline, batching, backend, phase-2

CC-41 — Implement Subtask Partitioning (inside each batch)
## Summary
Enable nested partitioning so each job batch can be further divided into subtasks, allowing complex workflows like record-level validation, scoring, or enrichment.

## Requirements
- Define subtask schema: subtask_id, parent_job_id, status, payload
- Support sequential or parallel execution modes
- Add subtask handling to scheduler (optional feature flag)
- Store partial subtask results for merge engine

## Deliverables
- SubtaskPartitioner module
- Subtask tables or JSONB field in community_jobs
- Scheduler enhancements to handle subtasks

## Acceptance Criteria
- Subtasks correctly tied to parent job
- Failure of one subtask does not corrupt batch
- Subtasks support merge + validation pipelines
- Orchestrator logs show subtask lifecycle events

## Suggested Labels
community-compute, data-pipeline, scheduler, backend, phase-2

CC-42 — Scale Orchestrator to Multi-Process / Multi-Worker Mode
## Summary
Upgrade the Community Compute Orchestrator so it can operate across multiple worker processes, threads, or containers, supporting horizontal scaling at high load.

## Requirements
- Support multi-process job assignment
- Ensure concurrency-safe job claiming (transaction-level locks required)
- Avoid race conditions between workers
- Enable optional distributed mode (Redis/postgres advisory locks)

## Deliverables
- OrchestratorWorker class
- Concurrency-safe job-claiming function
- Admin configuration for worker count

## Acceptance Criteria
- Two or more workers can run concurrently without double-claiming jobs
- Throughput scales linearly with number of workers
- Stress test proves safe operation under load
- Logs identify which worker handled which job

## Suggested Labels
community-compute, performance, scaling, backend, phase-2

CC-43 — Implement Distributed Normalization Workflow (cleaning raw data via compute nodes)
## Summary
Design a distributed normalization pipeline where compute nodes clean and standardize raw records (funder names, addresses, categories, EINs) according to canonical schemas.

## Requirements
- Define normalization schema and rule sets
- Create job types: normalize_funders, normalize_opportunities, normalize_locations
- Nodes execute normalization logic on batched input
- MergeEngine aligns normalized data into canonical tables

## Deliverables
- NormalizationPipeline module
- Ruleset JSON or Python functions
- Test data for normalization jobs

## Acceptance Criteria
- Raw data transformed into normalized, schema-compliant output
- Nodes can apply rules consistently
- Merge engine resolves collisions safely
- Normalization passes validation pipeline

## Suggested Labels
community-compute, data-pipeline, normalization, backend, phase-2

CC-44 — Implement Dataset Stitching Engine (combine multiple sources)
## Summary
Implement a stitching engine that merges outputs from different datasets (IRS, Grants.gov, foundation data, internal crawlers) into unified funder and opportunity profiles.

## Requirements
- Support stitching strategies:
  - EIN matching
  - fuzzy org-name matching
  - geographic matching
  - category alignment
- Track provenance (source-of-truth fields)
- Handle conflicting or ambiguous source data

## Deliverables
- DatasetStitcher module
- SourceProvenance model
- Validation for stitched records

## Acceptance Criteria
- IRS + Grants.gov + Foundation sources stitch into unified records
- Conflicts resolved by documented priority rules
- Provenance recorded for every stitched field
- Stitched output passes normalization validation

## Suggested Labels
community-compute, data-integration, matching, backend, phase-2

CC-45 — Implement Schema-Aware Merge Rules (field-level control)
## Summary
Add schema-aware merge rules enabling precise control of how individual fields behave when combining data from multiple nodes or multiple datasets.

## Requirements
- Field-level merge rules (overwrite, append, prefer-source, min/max, confidence-weighted)
- Integrate with MergeEngine + ValidationPipeline
- Define merge priorities in schema metadata
- Support versioned schema updates

## Deliverables
- MergeRulesEngine module
- Schema metadata describing merge behaviors
- Integration tests for merge rules

## Acceptance Criteria
- Merges consistent across multiple runs
- Field-level priorities respected
- Schema changes automatically adjust merge logic
- Admin debugging tools show why certain merges occurred

## Suggested Labels
community-compute, schema, merge-engine, backend, phase-2

CC-50 — Implement Domain Crawler Job Type (HTML fetch + parse)
## Summary
Create a Community Compute job type for distributed web crawling, enabling nodes to fetch, parse, and extract funder or opportunity information from permitted domains.

## Requirements
- Add new job_type: crawl_domain_page
- Job payload must include:
  - target_url
  - crawl_depth (optional)
  - extraction_rules (JSON)
- Node-side logic to fetch HTML, extract target fields, return JSON
- Must integrate with robots.txt validation and allow-list logic

## Deliverables
- CrawlerJobHandler module
- HTML extraction utility (BeautifulSoup or equivalent)
- Result schema for extracted fields

## Acceptance Criteria
- Nodes can fetch allowed pages and return structured JSON
- Extraction rules applied consistently
- Failed fetches trigger retry or abandonment logic
- Crawler jobs logged in orchestrator logs

## Suggested Labels
community-compute, crawling, data-extraction, backend, phase-2

CC-51 — Implement Robots.txt Enforcement Layer
## Summary
Implement strict robots.txt validation so compute nodes never crawl URLs that are disallowed. Must integrate with allow-list and domain policy tables.

## Requirements
- Parse and cache robots.txt per domain
- Store results in a robots_policy table or JSON field
- Validate requested URLs before sending jobs to nodes
- If disallowed:
  - cancel job or mark as invalid
  - update orchestrator logs
- Include UA string for EcoServants Compute Network

## Deliverables
- RobotsPolicy module
- robots_cache table or in-memory store
- Unit tests for common robots.txt formats

## Acceptance Criteria
- Disallowed URLs never reach compute nodes
- Robots.txt fetched responsibly and cached with TTL
- Orchestrator cancels invalid crawler tasks automatically
- Compliance documented clearly

## Suggested Labels
community-compute, crawling, compliance, backend, phase-2

CC-52 — Implement Sandbox Fetcher (Proxy Layer for Safe Node Crawling)
## Summary
Create a sandboxed network layer that routes all node crawl requests through a controlled proxy/fetcher to prevent malicious nodes from injecting harmful or unauthorized traffic.

## Requirements
- Proxy must validate:
  - domain allow-list
  - robots.txt rules
  - rate limits per domain
- Must sanitize request headers
- No direct outbound HTTP from nodes allowed
- Return sanitized HTML content to nodes

## Deliverables
- SandboxFetcher service
- Proxy configuration
- Integration with crawler job handler

## Acceptance Criteria
- Nodes never directly access external hosts
- Proxy enforces SSL, content length limits, and HTTP safety rules
- Malicious URLs blocked before fetching
- Sandbox logs capture all external requests

## Suggested Labels
community-compute, security, network, crawling, phase-2

CC-53 — Implement Domain Rate Limiting & Throttling Rules
## Summary
Add domain-level throttling to prevent overloading websites by distributing crawl jobs across time and nodes while respecting ethical online behavior.

## Requirements
- Track per-domain:
  - requests per minute
  - requests per hour
  - active crawler jobs
- Enforce delays between fetches
- Identify "too aggressive" nodes and apply backoff
- Integrate with SandboxFetcher and scheduler

## Deliverables
- DomainRateLimiter module
- New fields for domain usage metrics
- Throttle events in orchestrator logs

## Acceptance Criteria
- Domains never exceed configured crawl limits
- Multiple nodes throttled fairly
- Excessive crawling automatically paused
- Alerts raised when domain limits repeatedly hit

## Suggested Labels
community-compute, security, rate-limiting, crawling, phase-2

CC-54 — Implement Compute-Safe HTTP Client (node-side)
## Summary
Develop a minimal, secure HTTP client used by compute nodes for allowed fetch operations, removing unsafe capabilities and preventing misuse.

## Requirements
- Supports only GET requests
- Enforces:
  - max content size
  - max redirects
  - SSL verification
  - timeout limits
- Blocks:
  - POST/PUT/DELETE
  - IP-based hosts
  - local/internal addresses
- Provides sanitized HTML output

## Deliverables
- ComputeSafeHttpClient module
- Built-in validators for URL format + domain
- Unit tests for malicious URL attempts

## Acceptance Criteria
- Unsafe URLs rejected immediately
- Client cannot access internal or non-allowed networks
- All crawls go through trusted sandbox or proxy
- Node logs record safe-client activity

## Suggested Labels
community-compute, security, http-client, crawling, phase-2

CC-55 — Implement Extraction Rules Engine (CSS selectors + regex)
## Summary
Implement a rules engine for extracting structured data from crawled HTML using selectors, attributes, text patterns, and regex.

## Requirements
- Support:
  - CSS selectors
  - XPath (optional)
  - regex patterns for refinement
- Validate extraction rules server-side before sending to nodes
- Protect against malicious or runaway regex
- Output structured JSON per rule definition

## Deliverables
- ExtractionRulesEngine module
- Rule schema + validator
- Integration with crawler job handler

## Acceptance Criteria
- Extraction rules applied consistently across nodes
- Invalid rules rejected with error messages
- Engine scales to large HTML documents
- Output aligns with opportunity/funder schema

## Suggested Labels
community-compute, data-extraction, rules-engine, backend, phase-2

CC-60 — Implement Deep Extraction Job Type (multi-field structured scraping)
## Summary
Implement a job type designed for extracting multiple structured fields from complex HTML pages, supporting nested selectors, tables, lists, and hierarchical data.

## Requirements
- New job_type: extract_structured_fields
- Payload includes:
  - target_url
  - extraction_rules (multi-field schema)
  - fallback_rules (optional)
- Node output includes:
  - field_values
  - extraction_metadata
- Integrate with ValidationPipeline for schema compliance

## Deliverables
- StructuredExtractionHandler module
- Multi-field extraction rule schema
- Tests for nested DOM extraction

## Acceptance Criteria
- Complex pages with multiple fields extracted reliably
- Missing or malformed sections handled gracefully
- Output matches schema field definitions
- Extraction errors logged with full context

## Suggested Labels
community-compute, crawling, data-extraction, backend, phase-2

CC-61 — Implement Multi-Hop Crawling (following allowed in-domain links)
## Summary
Build a safe multi-hop crawler job that allows nodes to follow a limited number of allowed internal links to discover additional opportunity or funder pages.

## Requirements
- New job_type: crawl_multi_hop
- Payload includes:
  - start_url
  - max_hops
  - allowed_patterns
- Must obey:
  - robots.txt
  - domain allow-list
  - max page count
- Prevent infinite loops, cross-domain jumps, or recursive explosions

## Deliverables
- MultiHopCrawler module
- Link extraction + filtering logic
- Tests for hop limits and domain restrictions

## Acceptance Criteria
- Multi-hop crawl stays within domain boundaries
- Stops at hop limits or stop-pattern signals
- Extracts and returns discovered URLs safely
- Throttling and sandbox rules enforced per hop

## Suggested Labels
community-compute, crawling, multi-hop, backend, phase-2

CC-62 — Implement Document Fetching Job Type (PDFs, DOCs, etc.)
## Summary
Create a job type allowing nodes to download documents (PDF, DOCX, TXT) from approved domains via the Sandbox Fetcher for later text extraction.

## Requirements
- New job_type: fetch_document
- Fetch only from allow-listed domains
- Enforce:
  - max file size
  - safe MIME types
  - checksum validation
- Store document blob or return base64 payload

## Deliverables
- DocumentFetcher module
- MIME validator
- File size and extension rules

## Acceptance Criteria
- Nodes cannot fetch disallowed or unsafe file types
- Documents downloaded through sandbox only
- Large or suspicious files rejected safely
- Metadata stored with document fetch job results

## Suggested Labels
community-compute, data-ingestion, documents, backend, phase-2

CC-63 — Implement PDF Parsing Job Type (text + table extraction)
## Summary
Add distributed PDF parsing capabilities to extract text, tables, metadata, and structured sections from funding-related PDFs.

## Requirements
- New job_type: parse_pdf
- Node receives:
  - base64_pdf or pdf_url (via sandbox)
  - extraction_rules (optional)
- Use PDF parsing library for:
  - text extraction
  - table extraction
  - page-level metadata
- Output structured JSON normalized to schema

## Deliverables
- PDFParserJobHandler module
- PDF parsing library integration
- Tests for multi-page PDFs, tables, malformed files

## Acceptance Criteria
- PDF text extracted accurately across formats
- Tables extracted into normalized objects
- Parsing fails safely for corrupt PDFs
- Results validated before merge

## Suggested Labels
community-compute, pdf-processing, data-extraction, backend, phase-2

CC-64 — Implement Node Resource Budgeting (bandwidth + CPU limits)
## Summary
Introduce resource budgeting so compute nodes cannot exceed defined CPU, bandwidth, and memory usage during job execution.

## Requirements
- Define per-node resource budget:
  - max_bandwidth_per_min
  - max_cpu_time_per_job
  - max_memory_usage
- Enforce limits during crawling + PDF parsing
- Penalize nodes exceeding budgets
- Integrate with reputation + backoff systems

## Deliverables
- ResourceBudgetManager module
- Node resource tracking fields
- Enforcement hooks in job handlers

## Acceptance Criteria
- Nodes exceeding limits get throttled or penalized
- Resource use tracked accurately per job
- Budgets configurable via admin panel
- Prevents abusive or malfunctioning node behavior

## Suggested Labels
community-compute, security, resource-management, backend, phase-2

CC-65 — Implement Crawl Pipeline Analytics (domain stats + success rates)
## Summary
Add analytics to monitor crawling activity across domains, including success rates, extraction quality, error distribution, latency, and throughput.

## Requirements
- Track per-domain:
  - pages crawled
  - crawl success/failure counts
  - avg latency
  - extraction yield (fields found / fields requested)
- Create database table or metrics view
- Build admin analytics UI or API endpoint

## Deliverables
- CrawlAnalytics module
- Metrics table or view
- Dashboards or admin endpoints

## Acceptance Criteria
- Real-time statistics available for all crawler activity
- Domains with persistent failures detected quickly
- Analytics help optimize job rules + extraction strategies
- Metrics exportable for future BI dashboards

## Suggested Labels
community-compute, analytics, monitoring, backend, phase-2


CC-70 — Implement NLP Text Extraction Job (from HTML, PDF, DOCX)
## Summary
Implement a generalized NLP extraction job for turning unstructured documents (HTML, PDF, DOCX, TXT) into clean, normalized text suitable for downstream processing.

## Requirements
- New job_type: extract_text_nlp
- Input:
  - base64 document OR HTML source
  - metadata: source type, domain, language
- Processing:
  - strip boilerplate
  - remove menus, footers, duplicate text
  - normalize whitespace + encoding
- Output:
  - clean_text
  - extraction metadata (page count, confidence)

## Deliverables
- NLPTextExtractionHandler module
- Language detection support
- Tests for multiple file types

## Acceptance Criteria
- Clean text extracted from all supported formats
- Boilerplate consistently removed
- Language detection accurate for major languages
- Output passes ValidationPipeline checks

## Suggested Labels
community-compute, nlp, data-extraction, backend, phase-2

CC-71 — Implement Document Classification Job (categorize funding data)
## Summary
Add a job type allowing compute nodes to classify documents and web pages into categories such as “grant opportunity”, “funder profile”, “news”, or “irrelevant”.

## Requirements
- New job_type: classify_document
- Use lightweight ML or rules-based classification
- Input:
  - clean_text from CC-70
  - domain metadata
- Output:
  - category label
  - confidence score

## Deliverables
- DocumentClassifier module
- Category schema + label definitions
- Benchmark tests on internal sample set

## Acceptance Criteria
- Classifier identifies major categories with strong accuracy
- Low-confidence classifications flagged for review
- Classification metadata stored for enrichment workflows
- Admins can adjust classification rules

## Suggested Labels
community-compute, nlp, classification, backend, phase-2

CC-72 — Implement Entity Extraction Job (organizations, grants, people)
## Summary
Implement an entity extraction job that identifies organizations, opportunity names, contact persons, deadlines, and monetary values from text sources.

## Requirements
- New job_type: extract_entities
- Entity types:
  - organization
  - opportunity_title
  - deadline_date
  - monetary_amount
  - program_area
  - person_name (optional)
- Use regex + rule-based + ML-hybrid extraction
- Validate and normalize extracted entities

## Deliverables
- EntityExtractionEngine module
- Entity schema definitions
- Tests for varied entity formats

## Acceptance Criteria
- Entities extracted with consistent accuracy
- Dates, amounts, and names normalized to canonical schema
- Bad or misclassified entities quarantined for review
- Extracted entities integrate into dataset stitching

## Suggested Labels
community-compute, nlp, entity-extraction, backend, phase-2

CC-73 — Implement Deduplication & Entity Linking Job (cluster identical orgs)
## Summary
Create an entity linking job to merge duplicate funders or opportunities across datasets using string similarity, embeddings, and metadata signals.

## Requirements
- New job_type: link_entities
- Inputs:
  - normalized organizations
  - extracted entities (from CC-72)
- Outputs:
  - canonical_entity_id
  - confidence score
- Techniques:
  - fuzzy string match
  - TF-IDF or embeddings
  - geo/website metadata matching

## Deliverables
- EntityLinkingEngine module
- Deduplication pipeline with thresholds
- Validation tests for cluster quality

## Acceptance Criteria
- Duplicate organizations merged reliably
- Ambiguous matches flagged for human review
- Confidence scoring adjustable
- Linked entities ready for DatasetStitcher (CC-44)

## Suggested Labels
community-compute, nlp, matching, data-integration, backend, phase-2

CC-74 — Implement Opportunity Enrichment Job (add metadata via ML + rules)
## Summary
Add enrichment capabilities that enhance extracted opportunities with inferred metadata like eligibility flags, program focus, region, funding type, and tags.

## Requirements
- New job_type: enrich_opportunity
- Inputs:
  - normalized opportunity record
  - extracted text + entities
- Enrichment outputs:
  - inferred eligibility (org type, location)
  - thematic tags (environment, youth, research, etc.)
  - missing metadata completion (deadlines, fields of interest)
- Combine ML heuristics + rules-based inference

## Deliverables
- OpportunityEnrichmentEngine module
- Tagging schema
- Tests with real-world opportunity samples

## Acceptance Criteria
- Enriched metadata increases completeness and usability
- Incorrect inferences flagged with low confidence
- Output validated before merge/stitching
- Enrichment reproducible across nodes

## Suggested Labels
community-compute, nlp, enrichment, opportunity-search, backend, phase-2

CC-75 — Implement ML-Assisted Scoring Job (relevance + ranking)
## Summary
Build a scoring job that ranks opportunities based on relevance to EcoServants or end-user filters using lightweight ML models, semantic features, and structured metadata.

## Requirements
- New job_type: score_opportunity
- Scoring inputs:
  - normalized opportunity
  - enriched metadata (from CC-74)
  - entity links (from CC-73)
  - semantic similarity scores (optional future integration)
- Output:
  - relevance_score
  - scoring_explanation

## Deliverables
- OpportunityScoringEngine module
- Score weighting configuration file
- Unit tests for scoring consistency

## Acceptance Criteria
- Scoring results stable across nodes
- High relevance opportunities rise to top in evaluations
- Score explanations clear and interpretable
- Scores integrate with Opportunity Search API

## Suggested Labels
community-compute, nlp, ranking, ml, backend, phase-2


CC-80 — Implement Cross-Dataset Graph Builder (Funder–Opportunity Graph)
## Summary
Implement a distributed job that constructs a graph data model connecting funders, opportunities, locations, categories, and extracted entities across all datasets.

## Requirements
- New job_type: build_graph_relations
- Inputs:
  - stitched funder records
  - normalized opportunities
  - entity links (CC-73)
- Outputs:
  - graph edges: (funder → opportunity), (opportunity → category), (funder → geography), etc.
- Support for:
  - weighted edges (strength, frequency)
  - provenance tracking
- Nodes compute partial graph edges; orchestrator merges globally

## Deliverables
- GraphBuilder module
- Edge schema + metadata
- Merge pipeline for distributed graph outputs

## Acceptance Criteria
- Node outputs combine into a unified graph dataset
- Graph supports downstream ranking + clustering
- Graph edges validated for correctness and provenance
- Graph persists to database or graph store cleanly

## Suggested Labels
community-compute, graph, data-integration, backend, phase-2

CC-81 — Implement Relationship Inference Job (implicit links)
## Summary
Create a job type that identifies *implicit* relationships between entities based on textual similarity, co-occurrence, funding patterns, shared categories, or geographic overlap.

## Requirements
- New job_type: infer_relationships
- Detect relationships such as:
  - funders funding similar program areas
  - opportunities targeting overlapping beneficiary groups
  - cross-domain connections between scraped sources
- Use signals:
  - semantic similarity (optional)
  - tag overlap
  - shared entities (persons, locations, org names)

## Deliverables
- RelationshipInferenceEngine module
- Edge-strength scoring
- Tests using stitched dataset samples

## Acceptance Criteria
- Inferred links add meaningful structure to the dataset
- Low-confidence links quarantined for manual review
- Relationships integrate into graph built in CC-80
- Provenance stored with each inferred edge

## Suggested Labels
community-compute, graph, inference, backend, phase-2

CC-82 — Implement Network Analysis Jobs (centrality, clusters, communities)
## Summary
Add a distributed network analysis pipeline that runs graph algorithms like centrality ranking, clustering, community detection, and path scoring across the funder–opportunity graph.

## Requirements
- New job_type: graph_analysis
- Compute algorithms:
  - degree + weighted degree
  - PageRank-like importance
  - clustering coefficient
  - connected components / topic clusters
- Must support distributed computation across batches of edges

## Deliverables
- GraphAnalysisEngine module
- Algorithm implementations (or wrappers for graph libs)
- Result storage tables for graph metrics

## Acceptance Criteria
- Graph metrics computed consistently across nodes
- Clusters reflect logical thematic groupings (environmental, youth, research)
- Results integrate with search ranking engines
- Analysis tasks visible in analytics dashboard

## Suggested Labels
community-compute, graph, analytics, ranking, backend, phase-2

CC-83 — Implement Temporal Change Detection (detect dataset shifts over time)
## Summary
Implement a temporal analysis job that compares historical datasets to identify new funding trends, changed deadlines, removed opportunities, and shifts in funder behavior.

## Requirements
- New job_type: detect_temporal_changes
- Inputs:
  - dataset_version_n
  - dataset_version_(n-1)
- Detect changes:
  - new opportunities
  - updated funding amounts
  - changed eligibility criteria
  - closed or removed opportunities
- Output change events with metadata

## Deliverables
- TemporalChangeDetector module
- Diff schema for storing change events
- Visualization-ready structure for dashboards

## Acceptance Criteria
- Temporal diffs accurately reflect real dataset changes
- Noise minimization (e.g., ignore harmless formatting changes)
- Change logs integrated into admin view
- Temporal outputs feed into scoring + enrichment pipelines

## Suggested Labels
community-compute, analytics, temporal, backend, phase-2

CC-84 — Implement Dataset Version Diffing Engine (record-level diff)
## Summary
Create a diff engine for comparing any two versions of a dataset at a record level, tracking additions, modifications, deletions, and schema changes.

## Requirements
- New job_type: diff_dataset_versions
- Support field-level comparison
- Flag:
  - added records
  - removed records
  - changed fields (with before/after pairs)
- Apply schema-aware diff rules (CC-45)
- Store diffs as versioned JSON artifacts

## Deliverables
- DatasetDiffEngine module
- Diff schema definitions
- Result storage + indexing

## Acceptance Criteria
- Record-level differences identified with high precision
- Schema-aware comparisons respect merge rules
- Diff output readable by both humans and downstream processes
- Diffs validated as part of release workflow

## Suggested Labels
community-compute, versioning, diffing, backend, phase-2

CC-85 — Implement Dataset Integrity Audit Pipeline (full system audit)
## Summary
Implement a comprehensive audit pipeline that verifies dataset consistency, schema compliance, checksum correctness, provenance completeness, and graph coherence across all versions.

## Requirements
- New job_type: integrity_audit
- Validate:
  - referential integrity (no broken links)
  - checksum and signature consistency
  - schema completeness
  - missing provenance fields
  - graph edge correctness
- Produce audit report summarizing findings

## Deliverables
- IntegrityAuditEngine module
- Automated audit report generator
- Admin UI endpoint or downloadable JSON report

## Acceptance Criteria
- Audits catch missing or corrupted records before release
- No dataset can be published without passing integrity checks
- Reports include actionable error messages
- Audit pipeline integrated with CI/CD for dataset releases

## Suggested Labels
community-compute, auditing, integrity, backend, phase-2

