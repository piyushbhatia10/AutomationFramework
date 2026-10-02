import pytest

from quality_automation.api import assert_json_contract


@pytest.mark.api
def test_contract_helper_accepts_valid_payload() -> None:
    schema = {
        "type": "object",
        "required": ["id", "state"],
        "properties": {"id": {"type": "integer"}, "state": {"enum": ["active", "inactive"]}},
        "additionalProperties": False,
    }
    assert_json_contract({"id": 1, "state": "active"}, schema)
