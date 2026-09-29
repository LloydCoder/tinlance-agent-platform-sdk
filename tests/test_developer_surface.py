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


class _FakeRuns:
    def create(self, task_id, agent_id, intent, *, request_id=None):
        return (task_id, agent_id, intent, request_id)


class _FakeApprovals:
    def request(self, *args, **kwargs):
        return ("request", args, kwargs)

    def decide(self, *args, **kwargs):
        return ("decide", args, kwargs)


class _FakeClient:
    def __init__(self):
        self.runs = _FakeRuns()
        self.approvals = _FakeApprovals()


def test_agent_scaffold_delegates_run_creation() -> None:
    client = _FakeClient()
    scaffold = AgentScaffold(
        client,
        agent_id=UUID("11111111-1111-1111-1111-111111111111"),
        task_id=UUID("22222222-2222-2222-2222-222222222222"),
        spec=AgentSpec("Research", "1.0.0", "Governed research agent"),
    )
    assert scaffold.start("inspect", request_id="req-1")[2:] == ("inspect", "req-1")
    with pytest.raises(ValueError):
        scaffold.start("")


def test_approval_workflow_delegates_without_local_authority() -> None:
    workflow = ApprovalWorkflow(_FakeClient())
    request = ApprovalRequest(
        UUID("11111111-1111-1111-1111-111111111111"),
        "read",
        "repo:example",
        "review",
    )
    assert workflow.request(request)[0] == "request"
    assert workflow.decide(UUID("33333333-3333-3333-3333-333333333333"), True)[0] == "decide"


def test_trace_context_header_parsing_and_validation() -> None:
    context = TraceContext.from_headers(
        {"TraceParent": "00-11111111111111111111111111111111-2222222222222222-01"}
    )
    assert context is not None
    assert context.tracestate is None
    with pytest.raises(ValueError):
        TraceContext("00-00000000000000000000000000000000-2222222222222222-01")
    with pytest.raises(ValueError):
        TraceContext(
            "00-11111111111111111111111111111111-2222222222222222-01",
            "bad\nstate",
        )


def test_contract_and_lifecycle_validation_reject_invalid_values() -> None:
    with pytest.raises(ValueError):
        CapabilityDeclaration("", "1", "x")
    with pytest.raises(ValueError):
        IdempotencyKey("")
    assert not is_execution_terminal("not-a-state")
    with pytest.raises(ValueError):
        AgentSpec("", "1", "x")
    from tinlance_agent_platform_sdk.lifecycle import (
        validate_approval_state,
        validate_execution_state,
    )

    with pytest.raises(ValueError):
        validate_approval_state("not-a-state")
    with pytest.raises(ValueError):
        validate_execution_state("not-a-state")


def test_execution_result_retry_policy_covers_known_retryable_state() -> None:
    result = ExecutionResult(
        UUID("11111111-1111-1111-1111-111111111111"),
        "failed",
        "temporary",
        (),
        (),
        "temporary_failure",
        True,
    )
    assert result.terminal
    assert result.safe_to_retry
