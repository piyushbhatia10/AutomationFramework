"""Small command line interface for quality gates, dbt, and test-design assistance."""

from __future__ import annotations

import argparse
import sys

from quality_automation.ai import generate_test_design
from quality_automation.data import run_dbt_test
from quality_automation.reporting import evaluate_gate, load_report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qa-framework")
    commands = parser.add_subparsers(dest="command", required=True)
    gate = commands.add_parser("gate", help="Evaluate a generated quality report.")
    gate.add_argument("report")
    gate.add_argument("--minimum-pass-rate", type=float, default=0.98)
    gate.add_argument("--maximum-failed-tests", type=int, default=0)
    gate.add_argument("--coverage", type=float)
    gate.add_argument("--minimum-coverage", type=float)
    dbt = commands.add_parser("dbt-test", help="Run dbt test and preserve its output.")
    dbt.add_argument("--select")
    design = commands.add_parser("test-design", help="Generate a reviewable AI test-design proposal.")
    design.add_argument("--change", required=True)
    design.add_argument("--acceptance-criteria", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _build_parser().parse_args(argv)
    if arguments.command == "gate":
        violations = evaluate_gate(
            load_report(arguments.report),
            arguments.minimum_pass_rate,
            arguments.maximum_failed_tests,
            arguments.coverage,
            arguments.minimum_coverage,
        )
        if violations:
            print("QUALITY GATE FAILED")
            print("\n".join(f"- {violation}" for violation in violations))
            return 1
        print("QUALITY GATE PASSED")
        return 0
    if arguments.command == "dbt-test":
        result = run_dbt_test(arguments.select)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode
    if arguments.command == "test-design":
        print(generate_test_design(arguments.change, arguments.acceptance_criteria))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
