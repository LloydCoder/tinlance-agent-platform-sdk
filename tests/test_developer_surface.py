from uuid import UUID

import pytest

from tinlance_agent_platform_sdk import (
    AgentScaffold,
    AgentSpec,
    ApprovalRequest,
    ApprovalWorkflow,
    CapabilityDeclaration,
    ExecutionResult,
    IdempotencyKey,
    TraceContext,
    canonical_intent_fingerprint,
    is_execution_terminal,
)
from tinlance_agent_platform_sdk.errors import PlatformError


def test_official_developer_contracts_are_authority_neutral() -> None:
    capability = CapabilityDeclaration(
        capability_id="repository.read",
        version="1",
        description="Read repository content",
        scopes=("repo:example",),
        tool_names=("reference.echo",),
    )
    spec = AgentSpec("Research", "1.0.0", "Governed research agent", (capability,))
    assert spec.capabilities[0].as_payload()["capability_id"] == "repository.read"

    request = ApprovalRequest(
        UUID("11111111-1111-1111-1111-111111111111"),
        "read",
        "repo:example",
        "review",
    )
    assert request.as_payload()["run_id"].startswith("11111111")


def test_idempotency_and_fingerprint_are_deterministic() -> None:
    payload = {"tool": "reference.echo", "resource": "repo:example", "input": {"path": "README.md"}}
    assert canonical_intent_fingerprint(payload) == canonical_intent_fingerprint(dict(payload))
    key = IdempotencyKey.for_intent("tools.execute", payload)
    assert str(key).startswith("tl-")
    assert key == IdempotencyKey.for_intent("tools.execute", payload)


def test_trace_context_validates_and_propagates() -> None:
    context = TraceContext(
        "00-11111111111111111111111111111111-2222222222222222-01",
        "vendor=value",
    )
    headers = context.as_headers()
    assert headers["traceparent"].startswith("00-")
    assert headers["tracestate"] == "vendor=value"

    with pytest.raises(ValueError):
        TraceContext("ff-11111111111111111111111111111111-2222222222222222-01")


def test_execution_result_treats_unknown_outcome_as_non_retryable() -> None:
    result = ExecutionResult(
        UUID("11111111-1111-1111-1111-111111111111"),
        "outcome_unknown",
        None,
        (),
        (),
        "outcome_unknown",
        True,
    )
    assert result.terminal
    assert result.outcome_unknown
    assert not result.safe_to_retry
    assert is_execution_terminal(result.state)


def test_structured_platform_error_contains_no_secret() -> None:
    error = PlatformError(
        "request failed",
        status_code=403,
        error_code="forbidden",
        request_id="req-1",
        operation="tools.execute",
    )
    data = error.as_structured()
    assert data["code"] == "forbidden"
    assert data["request_id"] == "req-1"
    assert "secret" not in str(data).lower()


def test_agent_scaffold_and_approval_workflow_are_composition_only() -> None:
    assert AgentScaffold
    assert ApprovalWorkflow
