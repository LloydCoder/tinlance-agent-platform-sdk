from __future__ import annotations

import asyncio
from uuid import UUID

import pytest

from tinlance_agent_platform_sdk import (
    AsyncAgentPlatform,
    ClientConfig,
    ResearchAgent,
    ResearchRequest,
    ToolContractRegistry,
    ToolDescriptor,
    ToolInvocation,
)
from tinlance_agent_platform_sdk.models import ApprovalRef, Run


def test_client_config_rejects_insecure_default() -> None:
    with pytest.raises(ValueError):
        ClientConfig(
            base_url="http://example.com",
            bearer_token="token",
            tenant_id="tenant",
            subject_id="subject",
        )


def test_client_config_round_trips_client_kwargs() -> None:
    config = ClientConfig(
        base_url="http://example.com",
        bearer_token="token",
        tenant_id="tenant",
        subject_id="subject",
        allow_insecure_http=True,
        user_agent="tinlance-test/1",
    )
    kwargs = config.as_client_kwargs()
    assert kwargs["user_agent"] == "tinlance-test/1"
    assert kwargs["allow_insecure_http"] is True


def test_tool_contract_registry_is_metadata_only() -> None:
    registry = ToolContractRegistry()
    registry.register(ToolDescriptor("search", "research.read", "Search"))
    assert registry.list()[0].name == "search"
    with pytest.raises(ValueError):
        registry.register(ToolDescriptor("search", "research.read", "Duplicate"))


def test_tool_invocation_validates_required_fields() -> None:
    with pytest.raises(ValueError):
        ToolInvocation("", "capability", "action", "resource", {})
    with pytest.raises(ValueError):
        ToolInvocation("tool", "capability", "action", "resource", [])


def test_run_and_approval_models_are_immutable() -> None:
    run = Run(UUID("00000000-0000-0000-0000-000000000001"),
              UUID("00000000-0000-0000-0000-000000000002"),
              "running",
              UUID("00000000-0000-0000-0000-000000000003"))
    approval = ApprovalRef(UUID("00000000-0000-0000-0000-000000000004"))
    assert run.state == "running"
    assert approval.approval_id.int == 4
    with pytest.raises((AttributeError, TypeError)):
        run.state = "failed"  # type: ignore[misc]


def test_async_facade_reuses_sync_client() -> None:
    client = AsyncAgentPlatform(
        base_url="http://example.com",
        bearer_token="token",
        tenant_id="tenant",
        subject_id="subject",
        allow_insecure_http=True,
    )

    async def fake_health(*, request_id: str | None = None):
        return type("HealthValue", (), {"ready": True})()

    client._sync.health = fake_health  # type: ignore[method-assign]
    health = asyncio.run(client.health())
    assert health.ready is True


def test_research_request_requires_objective() -> None:
    with pytest.raises(ValueError):
        ResearchRequest(
            objective="",
            task_id=UUID("00000000-0000-0000-0000-000000000001"),
            agent_id=UUID("00000000-0000-0000-0000-000000000002"),
        )


def test_research_agent_delegates_to_platform(monkeypatch: pytest.MonkeyPatch) -> None:
    client = object.__new__(__import__(
        "tinlance_agent_platform_sdk.client", fromlist=["AgentPlatform"]
    ).AgentPlatform)

    class Runs:
        def create(self, task_id, agent_id, intent, *, request_id=None):
            assert task_id.int == 1
            assert agent_id.int == 2
            assert intent == "research:find evidence"
            assert request_id == "request-1"
            return Run(
                UUID("00000000-0000-0000-0000-000000000003"),
                task_id,
                "running",
                agent_id,
            )

    client.runs = Runs()  # type: ignore[attr-defined]
    result = ResearchAgent(client).start(
        ResearchRequest(
            "find evidence",
            UUID("00000000-0000-0000-0000-000000000001"),
            UUID("00000000-0000-0000-0000-000000000002"),
            "request-1",
        )
    )
    assert result.run.state == "running"
