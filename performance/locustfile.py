"""Example non-functional test. Run only against an approved non-production target."""

import os

from locust import HttpUser, between, task


class HealthCheckUser(HttpUser):
    host = os.getenv("PERFORMANCE_TARGET_URL", "https://example.test")
    wait_time = between(1, 3)

    @task
    def health_check(self) -> None:
        self.client.get("/health", name="GET /health")
