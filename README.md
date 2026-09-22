# Quality Automation Framework

A Python-first framework for engineering teams that need one quality layer across UI, APIs, contracts, data platforms, and delivery reporting. It is deliberately thin: test code stays ordinary `pytest`, while shared clients, assertions, reporting, quality gates, and AI-assisted test design remove repeated plumbing.

## What is included

- UI testing through Playwright page objects and fixtures.
- API and service testing through a typed HTTP client and JSON Schema contract checks.
- Data validation through portable SQL assertions and optional Snowflake, Redshift, and Databricks connectors.
- dbt test orchestration; Coalesce can run in its own CI job and publish its results into the same report directory.
- Machine-readable test-status reports and release quality gates.
- Optional AI test-design assistance that sends only the supplied change context to the configured provider.
- Templates for Locust performance checks and OWASP ZAP baseline scans.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,ui]'
playwright install chromium
cp framework.example.json framework.json
pytest --quality-report reports/quality-report.json
qa-framework gate reports/quality-report.json --minimum-pass-rate 0.98
```

Install only the warehouse integrations your project uses, for example `pip install -e '.[snowflake,dbt]'`. Copy `.env.example` to your team's secret store or CI environment; do not commit it.

## Test layout

```text
tests/
  api/          # endpoint behaviour and contract tests
  ui/           # page-object browser journeys
  data/         # SQL/data-quality validation
  contracts/    # JSON Schema documents
performance/    # Locust scenarios
security/       # ZAP configuration and scan artifacts
reports/        # generated outputs (ignored by Git)
```

Mark tests with `@pytest.mark.api`, `ui`, `data`, `performance`, or `security`. Run a layer with `pytest -m data` or compose a release suite with `pytest -m 'api or ui or data'`.

## Quality gate and report

The bundled pytest plugin writes `reports/quality-report.json`, including totals, failures, duration, and a pass rate. CI should upload it as an artifact and enforce it with `qa-framework gate`. Add `pytest --cov=your_package --cov-report=json` and pass the coverage percentage to the gate when coverage is a release requirement.

```bash
qa-framework gate reports/quality-report.json \
  --minimum-pass-rate 0.98 \
  --maximum-failed-tests 0 \
  --coverage 0.82 \
  --minimum-coverage 0.80
```

## AI-assisted engineering practices

Use AI before implementation and during review, never as an unverified test result:

1. Give it a small, non-sensitive change summary and acceptance criteria.
2. Ask for risks, equivalence classes, boundary cases, contracts, data lineage, and automation candidates.
3. Convert the output into reviewed pytest tests and schemas.
4. Keep the generated report and quality gate as the source of release evidence.

With `OPENAI_API_KEY` and `OPENAI_MODEL` set, run:

```bash
qa-framework test-design --change "Checkout now supports partial refunds" \
  --acceptance-criteria "Refund totals reconcile; unauthorised users receive 403"
```

No code, credentials, or production data are sent unless you include them in the two command arguments.

## Platform integration notes

- **Snowflake / Redshift / Databricks:** the `warehouse_connection()` factory reads credentials from environment variables and returns a DB-API compatible connection for SQL assertions.
- **dbt:** run `qa-framework dbt-test --select tag:critical` from the project containing `dbt_project.yml`.
- **Coalesce:** trigger its native job in CI, export its test/run result, and attach that artifact beside `quality-report.json`. This framework does not impersonate or store Coalesce credentials.
- **Performance:** customize `performance/locustfile.py`, then run `locust -f performance/locustfile.py --headless -u 20 -r 2 -t 2m`.
- **Security:** configure a permitted test target in `security/zap-baseline.conf` and run an authenticated ZAP baseline scan only against approved non-production environments.

## Suggested adoption path

Start with the highest-value API contracts and data reconciliation rules. Add one critical UI journey per release flow, then make the quality gate blocking only after its suite is stable. Treat coverage as a trend and pair it with failure rate, test duration, escaped defects, and data-quality rule pass rate; coverage alone is not quality.
