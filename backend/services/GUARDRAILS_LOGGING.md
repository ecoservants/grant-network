# Crawler Guardrail Violation Logging

## Overview
Crawler guardrails prevent unsafe crawling behavior such as
excessive depth, runaway page counts, circular link patterns,
and malformed job payloads.

All guardrail violations are logged for audit and monitoring.

---

## Logged Events

### Guardrail Violation
Triggered when a crawl job exceeds defined safety limits or
violates validation rules.

**Log Level:** WARNING  
**Stage:** crawler_guardrails  

**Fields**
- job_id
- current_url
- guardrail_type
  - payload_validation
  - depth_limit
  - page_limit
  - cycle_detection
- reason
- action = aborted

---

## Guarantees
- No crawl job can exceed configured limits
- Infinite or recursive crawls are stopped safely
- All safety violations are visible in orchestrator logs
