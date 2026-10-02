from __future__ import annotations

import os

import pytest

from quality_automation.api import ApiClient
from quality_automation.config import FrameworkConfig, load_config


@pytest.fixture(scope="session")
def framework_config() -> FrameworkConfig:
    return load_config()


@pytest.fixture(scope="session")
def api_client(framework_config: FrameworkConfig) -> ApiClient:
    return ApiClient(
        base_url=framework_config.api.base_url,
        token=os.getenv("QA_API_TOKEN"),
        timeout_seconds=framework_config.api.timeout_seconds,
    )


@pytest.fixture
def page(framework_config: FrameworkConfig):
    """Launch an isolated browser page when the optional UI dependency is installed."""
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as runner:
        browser = getattr(runner, framework_config.ui.browser).launch(headless=framework_config.ui.headless)
        browser_page = browser.new_page()
        yield browser_page
        browser.close()
