# Community Compute – Blocked Job Logging

## Overview
Community Compute enforces a preflight validation layer that blocks
non-compliant crawl and fetch jobs before dispatch.

All blocked jobs are explicitly logged for audit and compliance review.

---

## Logged Events

### 1. Preflight Validation Block
Triggered when a job violates domain allow-list or robots.txt policy.

**Log Level:** WARNING  
**Stage:** preflight_validation  

**Fields**
- job_id
- target_url
- policy_type (domain_policy | robots_policy)
- reason
- action = blocked

---

### 2. Job Rejection Before Dispatch
Triggered when a job is rejected by the scheduler.

**Log Level:** INFO  
**Stage:** scheduler  

**Fields**
- job_id
- target_url
- status = rejected
- failure_reason

---

## Compliance Guarantees
- Disallowed URLs never reach compute nodes
- robots.txt rules are enforced consistently
- All policy violations are visible in orchestrator logs
