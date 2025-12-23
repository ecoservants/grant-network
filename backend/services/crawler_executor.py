from crawler_guardrails import CrawlerGuardrails


class CrawlerExecutor:
    def __init__(self, crawler, logger):
        self.crawler = crawler
        self.logger = logger
        self.guardrails = CrawlerGuardrails(
            max_depth=10,
            max_pages=1000,
            logger=logger
        )

    def run(self, job):
        """
        Execute crawl job with safety guardrails enforced.
        """
        if not self.guardrails.validate_payload(job):
            job.status = "aborted"
            job.failure_reason = "Invalid crawl payload"
            return False

        visited_urls = set()
        pages_crawled = 0

        for current_depth, url in self.crawler.iter_urls(job.start_url):
            job.current_url = url

            if not self.guardrails.check_limits(job, current_depth, pages_crawled):
                job.status = "aborted"
                job.failure_reason = "Guardrail limit exceeded"
                return False

            if not self.guardrails.detect_cycle(job, visited_urls, url):
                job.status = "aborted"
                job.failure_reason = "Circular crawl detected"
                return False

            visited_urls.add(url)
            pages_crawled += 1
            self.crawler.fetch(url)

        return True
