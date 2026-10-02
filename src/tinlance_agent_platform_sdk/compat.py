"""Versioned Platform/SDK compatibility declarations.

The SDK is a consumer of the Platform contract. This module is intentionally
data-only: it does not infer capabilities from server behavior and it never
grants authority.
"""

from __future__ import annotations

SDK_VERSION = "0.1.0"
PLATFORM_API_VERSION = "1.1"
SUPPORTED_PLATFORM_API_VERSIONS = frozenset({PLATFORM_API_VERSION})

# Every public operation must have an expected response status. Keeping this
# manifest explicit makes accidental protocol expansion fail review/tests.
EXPECTED_SUCCESS_STATUS: dict[str, str] = {
    "health": "ok",
    "principal.get": "ok",
    "agents.list": "ok",
    "capabilities.list": "ok",
    "runs.create": "accepted",
    "runs.cancel": "accepted",
    "approvals.request": "accepted",
    "approvals.decide": "accepted",
    "tools.execute": "accepted",
    "executions.get": "ok",
    "runs.events": "ok",
    "runs.evidence": "ok",
}

PUBLIC_OPERATIONS = frozenset(EXPECTED_SUCCESS_STATUS)
DEFERRED_OPERATIONS = frozenset(
    {
        "runs.get",
        "runs.wait",
        "approvals.get",
        "approvals.approve",
        "approvals.reject",
        "approvals.cancel",
        "tools.list",
        "events.stream",
        "evidence.get",
        "pagination",
        "webhooks",
    }
)


def supports_platform_api(version: str) -> bool:
    """Return whether this SDK explicitly supports a Platform API version."""
    return version in SUPPORTED_PLATFORM_API_VERSIONS


def assert_contract_integrity() -> None:
    """Fail closed if the published operation manifests overlap or drift."""
    overlap = PUBLIC_OPERATIONS & DEFERRED_OPERATIONS
    if overlap:
        raise RuntimeError(f"operation is both public and deferred: {sorted(overlap)}")
    missing_status = PUBLIC_OPERATIONS - EXPECTED_SUCCESS_STATUS.keys()
    if missing_status:
        raise RuntimeError(f"public operations lack status contracts: {sorted(missing_status)}")
