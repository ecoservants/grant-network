"""
Crawler Guardrails Module

Prevents unsafe or runaway crawling by enforcing limits on
depth, page count, circular patterns, and payload validity.
"""

class CrawlerGuardrails:
    def __init__(
        self,
        max_depth: int,
        max_pages: int,
        logger
    ):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.logger = logger

    def validate_payload(self, job) -> bool:
        """
        Validate crawl job payload before execution.
        """
        if not job.start_url:
            self._log_violation(job, "Missing start_url", "payload_validation")
            return False

        if not isinstance(job.max_depth, int) or job.max_depth < 0:
            self._log_violation(job, "Invalid max_depth", "payload_validation")
            return False

        if not isinstance(job.max_pages, int) or job.max_pages <= 0:
            self._log_violation(job, "Invalid max_pages", "payload_validation")
            return False

        return True

    def check_limits(self, job, current_depth, pages_crawled) -> bool:
        """
        Enforce crawl depth and page limits during execution.
        """
        if current_depth > min(job.max_depth, self.max_depth):
            self._log_violation(job, "Max crawl depth exceeded", "depth_limit")
            return False

        if pages_crawled > min(job.max_pages, self.max_pages):
            self._log_violation(job, "Max pages per crawl exceeded", "page_limit")
            return False

        return True

    def detect_cycle(self, job, visited_urls, next_url) -> bool:
        """
        Detect circular or recursive crawl patterns.
        """
        if next_url in visited_urls:
            self._log_violation(job, "Circular link pattern detected", "cycle_detection")
            return False

        return True

    def _log_violation(self, job, reason: str, guardrail_type: str):
        self.logger.warning(
            "Crawler guardrail violation detected",
            extra={
                "stage": "crawler_guardrails",
                "job_id": getattr(job, "id", None),
                "url": getattr(job, "current_url", None),
                "guardrail_type": guardrail_type,
                "reason": reason,
                "action": "aborted"
            }
        )
