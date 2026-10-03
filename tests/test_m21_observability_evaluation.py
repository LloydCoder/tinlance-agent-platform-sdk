import pytest

from tinlance_agent_platform_sdk import (
    EvaluationAssertion,
    EvaluationCase,
    EvaluationResult,
    safe_attributes,
)


def test_safe_agent_observability_attributes_are_allow_listed() -> None:
    attrs = safe_attributes(
        operation="tools.execute",
        request_id="req-1",
        status_code=200,
        elapsed_ms=12.5,
    )
    assert attrs["tinlance.operation"] == "tools.execute"
    assert "authorization" not in attrs
    assert "prompt" not in attrs
    assert "payload" not in attrs
    assert "secret" not in attrs


def test_evaluation_references_preserve_unknown_without_scoring_engine() -> None:
    case = EvaluationCase("case-1", "1", "R10 evidence", ("evidence exists",))
    result = EvaluationResult(
        case_id=case.case_id,
        outcome="unknown",
        assertions=(EvaluationAssertion("evidence exists", None, "not-observed"),),
        evidence_references=("evidence:123",),
        trace_references=("trace:123",),
    )
    assert result.passed is None
    assert result.outcome == "unknown"


def test_evaluation_reference_validation_is_fail_closed() -> None:
    with pytest.raises(ValueError):
        EvaluationCase("", "1", "invalid")
    with pytest.raises(ValueError):
        EvaluationAssertion("", None)

    with pytest.raises(ValueError):
        EvaluationAssertion("valid", None, "")

    with pytest.raises(ValueError):
        EvaluationCase("case", "1", "name", ("",))

    with pytest.raises(ValueError):
        EvaluationResult("", "unknown")

    with pytest.raises(ValueError):
        EvaluationResult("case", "unknown", evidence_references=("",))

    with pytest.raises(ValueError):
        EvaluationResult("case", "unknown", trace_references=("",))
