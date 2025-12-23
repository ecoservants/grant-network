"""
Preflight Validation Module

Validates crawl and fetch jobs against domain allow-list
and robots.txt rules before any job is dispatched.
"""

from urllib.parse import urlparse
from typing import Tuple


class PreflightValidation:
    def __init__(self, domain_policy, robots_policy, logger):
        self.domain_policy = domain_policy
        self.robots_policy = robots_policy
        self.logger = logger

    def validate(self, job) -> Tuple[bool, str]:
        """
        Run all preflight checks.
        Returns (allowed: bool, reason: str)
        """
        target_url = job.target_url
        domain = urlparse(target_url).netloc

        # Domain allow-list validation
        if not self.domain_policy.is_allowed(domain):
            reason = f"Domain not allow-listed: {domain}"
            self._log_block(job, reason, "domain_policy")
            return False, reason

        # robots.txt validation
        if not self.robots_policy.is_allowed(target_url):
            reason = f"Blocked by robots.txt rules: {target_url}"
            self._log_block(job, reason, "robots_policy")
            return False, reason

        return True, "Preflight validation passed"

    def _log_block(self, job, reason: str, policy_type: str):
        self.logger.warning(
            "Preflight validation blocked job",
            extra={
                "stage": "preflight_validation",
                "job_id": getattr(job, "id", None),
                "url": job.target_url,
                "policy_type": policy_type,
                "reason": reason,
                "action": "blocked"
            }
        )
