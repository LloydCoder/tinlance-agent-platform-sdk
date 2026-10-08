#!/usr/bin/env python3
"""Fail-closed verification of SDK compatibility with the canonical TSIC contract."""

from __future__ import annotations

import json
from urllib.request import Request, urlopen

TSIC_REVISION = "bdb5b7f9f2295562ad8681c591a8a927500b4d8c"
RAW_ROOT = (
    f"https://raw.githubusercontent.com/LloydCoder/tinlance-system-integration/{TSIC_REVISION}"
)
REQUIRED = {
    "identity-context",
    "agent-registration",
    "delivery-semantics",
    "trace-context",
    "agent-interoperability-gate",
    "economic-attribution",
}


def fetch_json(path: str) -> dict:
    request = Request(
        f"{RAW_ROOT}/{path}",
        headers={
            "Accept": "application/json",
            "User-Agent": "tinlance-agent-platform-sdk-ci",
        },
    )
    with urlopen(request, timeout=15) as response:
        if response.status != 200:
            raise RuntimeError(f"TSIC contract fetch failed for {path}: HTTP {response.status}")
        return json.load(response)


def main() -> None:
    manifest = fetch_json("manifests/ecosystem.json")
    adapter = fetch_json("integrations/agent-platform-sdk/adapter.json")
    registry = fetch_json("catalog/contracts/registry.json")

    sdk = next(item for item in manifest["systems"] if item["id"] == "agent-platform-sdk")
    if sdk["repository"] != "LloydCoder/tinlance-agent-platform-sdk":
        raise AssertionError("TSIC SDK repository mapping is stale")
    if sdk.get("governance_role") != "developer_client_surface":
        raise AssertionError("TSIC SDK governance role is incorrect")

    if adapter["source_system"] != "tsic" or adapter["target_system"] != "agent-platform-sdk":
        raise AssertionError("invalid TSIC SDK adapter endpoints")
    bindings = {item["tsic_contract"] for item in adapter["contract_bindings"]}
    if bindings != REQUIRED:
        raise AssertionError(
            f"TSIC SDK binding drift: expected {sorted(REQUIRED)}, got {sorted(bindings)}"
        )

    registered = {item["id"] for item in registry["contracts"]}
    if not registered >= REQUIRED:
        raise AssertionError("TSIC registry is missing an SDK contract")

    authority = adapter["authority"]
    if authority["integration_contracts"] != "tsic":
        raise AssertionError("TSIC must remain integration-contract authority")
    if authority["developer_surface"] != "agent-platform-sdk":
        raise AssertionError("SDK developer surface authority drift")
    if authority["execution_authority"] != "agent-platform":
        raise AssertionError("Platform execution authority drift")

    invariants = set(adapter["invariants"])
    required_invariants = {
        "sdk_never_grants_execution_authority",
        "sdk_never_authorizes_side_effects",
        "tenant_context_is_immutable",
        "authenticated_principal_is_platform_authoritative",
        "trace_context_is_preserved",
        "idempotency_metadata_is_preserved",
    }
    if invariants != required_invariants:
        raise AssertionError("TSIC SDK invariant drift")

    print(
        "PASS TSIC SDK conformance:",
        f"revision={TSIC_REVISION} contracts={len(bindings)}",
    )


if __name__ == "__main__":
    main()
