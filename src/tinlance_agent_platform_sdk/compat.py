"""Compatibility and feature declarations for the external SDK."""

from __future__ import annotations

SDK_VERSION = "0.1.0"
SUPPORTED_PLATFORM_API_VERSIONS = frozenset({"1.1"})
PUBLIC_OPERATIONS = frozenset(
    {
        "health",
        "principal.get",
        "agents.list",
        "capabilities.list",
        "runs.create",
        "runs.cancel",
        "approvals.request",
        "approvals.decide",
        "tools.execute",
        "executions.get",
        "runs.events",
        "runs.evidence",
    }
)
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
    return version in SUPPORTED_PLATFORM_API_VERSIONS
