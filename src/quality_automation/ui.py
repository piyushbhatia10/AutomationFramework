"""Minimal page-object base class for readable, reusable browser journeys."""

from __future__ import annotations

from typing import Any


class BasePage:
    def __init__(self, page: Any, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def visit(self, path: str = "/") -> None:
        self.page.goto(f"{self.base_url}/{path.lstrip('/')}")

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()
