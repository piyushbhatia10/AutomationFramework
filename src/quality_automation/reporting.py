"""Test report model and release quality gate evaluation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
import json
from typing import Any


@dataclass(frozen=True)
class TestResult:
    nodeid: str
    outcome: str
    duration_seconds: float
    error: str | None = None
    layers: tuple[str, ...] = ()


def create_report(results: list[TestResult], started_at: datetime) -> dict[str, Any]:
    totals = {"passed": 0, "failed": 0, "skipped": 0, "other": 0}
    for result in results:
        totals[result.outcome if result.outcome in totals else "other"] += 1
    executed = totals["passed"] + totals["failed"]
    by_layer: dict[str, dict[str, int]] = {}
    for result in results:
        for layer in result.layers:
            layer_totals = by_layer.setdefault(
                layer, {"passed": 0, "failed": 0, "skipped": 0, "other": 0, "total": 0}
            )
            layer_totals[result.outcome if result.outcome in totals else "other"] += 1
            layer_totals["total"] += 1
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "started_at": started_at.astimezone(UTC).isoformat(),
        "duration_seconds": round(sum(result.duration_seconds for result in results), 3),
        "totals": {**totals, "total": len(results)},
        "pass_rate": round(totals["passed"] / executed, 4) if executed else None,
        "by_layer": by_layer,
        "tests": [asdict(result) for result in results],
    }


def write_report(path: str | Path, report: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def load_report(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as file:
        return json.load(file)


def evaluate_gate(
    report: dict[str, Any],
    minimum_pass_rate: float,
    maximum_failed_tests: int,
    coverage: float | None = None,
    minimum_coverage: float | None = None,
) -> list[str]:
    """Return violations; an empty list means the release quality gate passed."""
    totals = report["totals"]
    violations: list[str] = []
    pass_rate = report.get("pass_rate")
    if pass_rate is None:
        violations.append("No executed tests were present in the report.")
    elif pass_rate < minimum_pass_rate:
        violations.append(f"Pass rate {pass_rate:.2%} is below {minimum_pass_rate:.2%}.")
    failed = int(totals.get("failed", 0))
    if failed > maximum_failed_tests:
        violations.append(f"Failed tests {failed} exceed the allowed {maximum_failed_tests}.")
    if minimum_coverage is not None:
        if coverage is None:
            violations.append("Coverage is required by this gate but was not supplied.")
        elif coverage < minimum_coverage:
            violations.append(f"Coverage {coverage:.2%} is below {minimum_coverage:.2%}.")
    return violations
