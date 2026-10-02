"""Pytest plugin that turns individual results into a portable status report."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from quality_automation.reporting import TestResult, create_report, write_report


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("quality automation")
    group.addoption(
        "--quality-report",
        action="store",
        default="reports/quality-report.json",
        help="Path for the generated machine-readable status report.",
    )


def pytest_configure(config: pytest.Config) -> None:
    config._quality_started_at = datetime.now(UTC)  # type: ignore[attr-defined]
    config._quality_results = []  # type: ignore[attr-defined]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    """Capture call-phase reports while the pytest config is still available."""
    outcome = yield
    report: pytest.TestReport = outcome.get_result()
    # A skipped fixture produces a setup-phase report and no call phase, so
    # include it without double-counting normal successful setup reports.
    if report.when != "call" and not (report.when == "setup" and report.skipped):
        return
    config = item.config
    error = report.longreprtext[:2000] if report.failed else None
    layers = tuple(
        marker.name
        for marker in item.iter_markers()
        if marker.name in {"api", "ui", "data", "performance", "security"}
    )
    config._quality_results.append(  # type: ignore[attr-defined]
        TestResult(report.nodeid, report.outcome, report.duration, error, layers)
    )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    config = session.config
    report = create_report(
        config._quality_results,  # type: ignore[attr-defined]
        config._quality_started_at,  # type: ignore[attr-defined]
    )
    report["pytest_exit_status"] = exitstatus
    write_report(config.getoption("quality_report"), report)
