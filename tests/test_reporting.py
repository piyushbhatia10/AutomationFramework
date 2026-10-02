from datetime import UTC, datetime

from quality_automation.reporting import TestResult, create_report, evaluate_gate


def test_quality_gate_reports_failure() -> None:
    report = create_report(
        [TestResult("tests/test_a.py::test_a", "passed", 0.1), TestResult("tests/test_b.py::test_b", "failed", 0.2)],
        datetime.now(UTC),
    )
    violations = evaluate_gate(report, minimum_pass_rate=0.98, maximum_failed_tests=0)
    assert len(violations) == 2
