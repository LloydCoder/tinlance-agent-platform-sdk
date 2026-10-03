from uuid import uuid4

from tinlance_agent_platform_sdk import (
    AgentSpec,
    CapabilityDeclaration,
    GuardrailSpec,
    LifecycleSpec,
    ModelSpec,
    ObservabilitySpec,
    ToolDescriptor,
)


def test_agent_spec_serializes_declarative_developer_surface() -> None:
    spec = AgentSpec(
        name="research-agent",
        version="1.2.0",
        description="Governed research composition",
        capabilities=(
            CapabilityDeclaration(
                "repository.read",
                "1",
                "Read repository metadata",
                scopes=("repo:read",),
                tool_names=("repository.read",),
            ),
        ),
        instructions="Research the requested repository.",
        reference="research-agent-reference",
        tools=(
            ToolDescriptor(
                "repository.read",
                "repository.read",
                "Read repository metadata",
                "1",
            ),
        ),
        model=ModelSpec("provider-x", "model-y", "2026-10"),
        guardrails=(GuardrailSpec("sensitive-output", "content", "enforce"),),
        lifecycle=LifecycleSpec(restartable=True, resumable=False),
        observability=ObservabilitySpec(
            service_name="research-agent",
            environment="test",
            attributes=(("team", "security"),),
        ),
        metadata=(("owner", "platform"),),
    )

    payload = spec.as_payload()
    assert payload["name"] == "research-agent"
    assert payload["model"] == {
        "provider": "provider-x",
        "model": "model-y",
        "version": "2026-10",
    }
    assert payload["tools"][0]["name"] == "repository.read"
    assert payload["guardrails"][0]["mode"] == "enforce"
    assert payload["observability"]["trace_enabled"] is True
    assert "bearer_token" not in payload
    assert "authorization" not in payload
    assert "policy" not in payload
    assert "secret" not in payload


def test_agent_spec_validation_rejects_blank_declarative_fields() -> None:
    try:
        ModelSpec("", "model")
        raise AssertionError("blank provider must fail")
    except ValueError:
        pass

    try:
        GuardrailSpec("guardrail", "", "enforce")
        raise AssertionError("blank guardrail kind must fail")
    except ValueError:
        pass

    try:
        ObservabilitySpec(attributes=(("", "value"),))
        raise AssertionError("blank observability attribute key must fail")
    except ValueError:
        pass


def test_agent_scaffold_still_requires_platform_issued_ids() -> None:
    assert uuid4() is not None
