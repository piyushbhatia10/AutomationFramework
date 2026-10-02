"""Optional, explicit AI assistance for test design. It never runs tests or gates releases."""

from __future__ import annotations

import os


def test_design_prompt(change: str, acceptance_criteria: str) -> str:
    return f"""You are a senior quality engineer. Create a concise, reviewable test-design proposal.

Change summary:
{change}

Acceptance criteria:
{acceptance_criteria}

Return sections for: risks and assumptions; API/service and contract cases; UI journeys; data/SQL validation rules; negative and boundary cases; performance and security considerations; automation priority. Do not invent system behaviour. Flag ambiguities as questions. Never include secrets, personal data, or production payloads."""


def generate_test_design(change: str, acceptance_criteria: str) -> str:
    """Call an OpenAI-compatible SDK only when the caller configured it explicitly."""
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")
    if not api_key or not model:
        raise RuntimeError("Set OPENAI_API_KEY and OPENAI_MODEL to use AI test design.")
    try:
        from openai import OpenAI  # type: ignore[import-not-found]
    except ImportError as error:
        raise RuntimeError("Install the optional AI dependency: pip install -e '.[ai]'") from error
    response = OpenAI(api_key=api_key).responses.create(model=model, input=test_design_prompt(change, acceptance_criteria))
    return response.output_text
