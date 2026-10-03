import json
from pathlib import Path

import tomllib

import tinlance_agent_platform_sdk as sdk


def test_m21_7_release_metadata_is_reconciled() -> None:
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    manifest = json.loads(
        Path("docs/contracts/sdk-contract-manifest.json").read_text(encoding="utf-8")
    )
    compatibility = json.loads(
        Path("docs/contracts/compatibility-matrix.json").read_text(encoding="utf-8")
    )
    assert project["project"]["version"] == "1.0.0"
    assert sdk.SDK_VERSION == "1.0.0"
    assert manifest["sdk_version"] == "1.0.0"
    assert compatibility["sdk_version"] == "1.0.0"
    assert manifest["platform_api_version"] == "1.1"


def test_m21_7_public_operation_set_matches_manifest() -> None:
    manifest = json.loads(
        Path("docs/contracts/sdk-contract-manifest.json").read_text(encoding="utf-8")
    )
    assert set(sdk.PUBLIC_OPERATIONS) == set(manifest["operations"])
    assert set(sdk.DEFERRED_OPERATIONS) == set(manifest["deferred_operations"])
    assert "runs.resume" not in sdk.PUBLIC_OPERATIONS


def test_m21_7_release_workflow_contains_integrity_gates() -> None:
    workflow = Path(".github/workflows/release.yml").read_text(encoding="utf-8")
    for marker in (
        "python -m build",
        "Smoke-test wheel installation",
        "python -m twine check dist/*",
        "actions/attest-build-provenance",
        "id-token: write",
        "gh-action-pypi-publish",
    ):
        assert marker in workflow


def test_m21_7_enterprise_docs_are_present() -> None:
    for path in (
        "docs/M21.1.md",
        "docs/M21.2.md",
        "docs/M21.3.md",
        "docs/M21.4.md",
        "docs/M21.5.md",
        "docs/M21.6.md",
        "docs/M21.7.md",
        "docs/security/m21-6-control-matrix.json",
    ):
        assert Path(path).is_file()
