from tinlance_agent_platform_sdk.features import (
    PAGINATION,
    STREAMING,
    WEBHOOKS,
    deferred_capabilities,
)


def test_streaming_is_explicitly_contract_gated() -> None:
    assert STREAMING.name == "events.stream"
    assert STREAMING.required_platform_contract == "platform.events.stream.v1"
    assert "not" in STREAMING.reason.lower() or "no" in STREAMING.reason.lower()


def test_deferred_capability_registry_is_complete_and_immutable() -> None:
    capabilities = deferred_capabilities()
    assert capabilities == (STREAMING, PAGINATION, WEBHOOKS)
    assert tuple(capability.name for capability in capabilities) == (
        "events.stream",
        "pagination",
        "webhooks",
    )
