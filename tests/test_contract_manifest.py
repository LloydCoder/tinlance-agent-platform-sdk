import json

from pathlib import Path

from tinlance_agent_platform_sdk.compat import DEFERRED_OPERATIONS, EXPECTED_SUCCESS_STATUS


def test_language_neutral_contract_manifest_matches_python_surface() -> None:
    path = Path("docs/contracts/sdk-contract-manifest.json")
    manifest = json.loads(path.read_text())
    assert manifest["platform_api_version"] == "1.1"
    assert manifest["operations"] == EXPECTED_SUCCESS_STATUS
    assert frozenset(manifest["deferred_operations"]) == DEFERRED_OPERATIONS
    assert manifest["generation_rules"]["authority"] == "platform-only"
