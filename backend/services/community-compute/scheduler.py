from preflight_validation import PreflightValidation


class Scheduler:
    def __init__(self, queue, domain_policy, robots_policy, logger):
        self.queue = queue
        self.logger = logger
        self.preflight = PreflightValidation(
            domain_policy=domain_policy,
            robots_policy=robots_policy,
            logger=logger
        )

    def schedule_job(self, job) -> bool:
        """
        Validate and schedule a job.
        Jobs failing preflight are rejected before dispatch.
        """
        allowed, reason = self.preflight.validate(job)

        if not allowed:
            job.status = "rejected"
            job.failure_reason = reason

            self.logger.info(
                "Job rejected before dispatch",
                extra={
                    "stage": "scheduler",
                    "job_id": job.id,
                    "url": job.target_url,
                    "status": "rejected",
                    "failure_reason": reason
                }
            )
            return False

        self.queue.enqueue(job)
        return True
