import pytest

from quality_automation.ui import BasePage


@pytest.mark.ui
def test_homepage_has_expected_title(page, framework_config) -> None:
    """Replace this starter journey with a product-specific page object and assertions."""
    if not framework_config.ui.base_url:
        pytest.skip("Set ui.base_url in framework.json to enable UI journeys.")
    BasePage(page, framework_config.ui.base_url).visit()
    assert page.title(), "Expected the homepage to define a document title"
