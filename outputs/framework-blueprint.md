# Framework blueprint

The delivered project is a Python quality-automation foundation located at:

`/Users/pc/Documents/Codex/2026-09-20/i-want-to-build-my-own`

It uses ordinary `pytest` tests with shared framework components, so individual applications can adopt only the capabilities they need.

| Capability | Included foundation | Team-specific next decision |
| --- | --- | --- |
| UI | Playwright fixture and reusable page-object base | Critical journeys and test accounts |
| API and contracts | HTTP client and JSON Schema assertions | API inventory and schema ownership |
| Data | Portable SQL rules plus Snowflake, Redshift, and Databricks factories | Read-only credentials and canonical reconciliation queries |
| Transformations | dbt test command integration | dbt selectors, model criticality, and Coalesce job/artifact workflow |
| Non-functional | Locust and OWASP ZAP templates | Approved non-production targets and thresholds |
| Reporting | JSON report, per-layer metrics, and CI quality gate | Release thresholds, dashboard destination, and trend baselines |
| AI delivery | Explicit, opt-in test-design workflow | Approved model, data-handling policy, and review ownership |

## Recommended rollout

1. Connect a non-production environment and implement three high-value API contracts plus two data reconciliation rules.
2. Add one browser journey for the highest-risk customer flow. Keep it small and deterministic.
3. Run these suites in pull requests, publish `reports/quality-report.json`, and observe the signal for two releases.
4. Make the gate blocking once test ownership, fixtures, data refresh, and failure triage are stable.
5. Add performance and security jobs after targets, authentication, and thresholds are explicitly approved.

## First local command

```bash
cd /Users/pc/Documents/Codex/2026-09-20/i-want-to-build-my-own
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,ui]'
playwright install chromium
cp framework.example.json framework.json
pytest --quality-report reports/quality-report.json
```
