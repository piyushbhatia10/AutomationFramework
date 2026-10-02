"""API and contract test helpers."""

from __future__ import annotations

from typing import Any

import requests
from jsonschema import Draft202012Validator


class ApiClient:
    def __init__(self, base_url: str, token: str | None = None, timeout_seconds: float = 20.0):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        response = self.session.request(
            method=method,
            url=f"{self.base_url}/{path.lstrip('/')}",
            timeout=kwargs.pop("timeout", self.timeout_seconds),
            **kwargs,
        )
        return response

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", path, **kwargs)


def assert_status(response: requests.Response, expected: int) -> None:
    assert response.status_code == expected, (
        f"Expected HTTP {expected}, received {response.status_code}: {response.text[:500]}"
    )


def assert_json_contract(instance: Any, schema: dict[str, Any]) -> None:
    """Validate a response body against a versioned JSON Schema."""
    errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda error: list(error.path))
    assert not errors, "Contract validation failed:\n" + "\n".join(error.message for error in errors)
