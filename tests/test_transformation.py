from uuid import UUID

import pytest

from tinlance_agent_platform_sdk import (
    Transformation,
    TransformationConstraints,
    TransformationMetric,
    TransformationOutcome,
    TransformationProvenance,
    TransformationReference,
)


def make_transformation() -> Transformation:
    return Transformation(
        transformation_id=UUID("2f6d7a8a-5a12-4f8b-9a3e-3c1c2f4d8e11"),
        tenant_ref="tenant:example",
        version=1,
        objective="Reduce reconciliation cycle time",
        success_criteria=("Produce a reconciled report",),
        principal_ref="principal:human-001",
        agent_ref="agent:finance-reconciliation",
        agent_version="1.0.0",
        workspace_ref="workspace:finance",
        task_ref="task:reconciliation-001",
        requested_capabilities=(("capability:finance.reconcile", "required"),),
        policy_refs=("policy:finance.reconciliation",),
        risk_class="high",
        idempotency_key="transformation-2f6d7a8a-v1",
        execution_state="succeeded",
        run_ref="run:001",
        output_refs=(TransformationReference("artifact:report", "report"),),
        evidence_refs=(TransformationReference("evidence:run", "execution"),),
        outcome=TransformationOutcome(
            "achieved",
            True,
            metrics=(TransformationMetric("cycle_hours", 2, "hours"),),
            business_effect_refs=("effect:reduced-close-time",),
        ),
        deadline="2026-10-18T00:00:00Z",
        budget_ref="budget:task-001",
        data_classification="confidential",
        resource_refs=("resource:ledger",),
        approval_refs=("approval:001",),
        source_refs=("source:request-001",),
        started_at="2026-10-17T17:00:00Z",
        completed_at="2026-10-17T17:02:00Z",
        provenance=TransformationProvenance(
            declared_by="tadl:p1",
            recorded_at="2026-10-17T17:02:01Z",
            source_refs=("source:request-001",),
        ),
    )


def test_transformation_payload_is_authority_neutral() -> None:
    transformation = make_transformation()
    payload = transformation.as_payload()
    assert payload["schema_version"] == "transformation/v1"
    assert "authorization_decision" not in payload
    assert "capability_grant" not in payload
    assert payload["provenance"]["declared_by"] == "tadl:p1"
    assert payload["provenance"]["recorded_at"] == "2026-10-17T17:02:01Z"
    assert payload["constraints"]["budget_ref"] == "budget:task-001"
    assert payload["constraints"]["data_classification"] == "confidential"
    assert payload["governance"]["approval_refs"] == ["approval:001"]
    assert payload["execution"]["started_at"] == "2026-10-17T17:00:00Z"
    assert payload["execution"]["completed_at"] == "2026-10-17T17:02:00Z"
    assert transformation.content_digest() == transformation.content_digest()


def test_transformation_rejects_weak_idempotency() -> None:
    with pytest.raises(ValueError):
        make_transformation().__class__(
            transformation_id=make_transformation().transformation_id,
            tenant_ref="tenant:example",
            version=1,
            objective="x",
            success_criteria=("x",),
            principal_ref="p",
            agent_ref="a",
            agent_version="1",
            workspace_ref="w",
            task_ref="t",
            requested_capabilities=(("c", "r"),),
            policy_refs=("p",),
            risk_class="low",
            idempotency_key="short",
        )



def test_transformation_rejects_contradictory_outcome_status() -> None:
    with pytest.raises(ValueError):
        TransformationOutcome("achieved", False)
    with pytest.raises(ValueError):
        TransformationOutcome("partially_achieved", True)


def test_transformation_provenance_requires_timezone() -> None:
    with pytest.raises(ValueError):
        TransformationProvenance(
            declared_by="tadl:p1",
            recorded_at="2026-10-17T17:02:01",
        )


def test_transformation_constraints_are_preserved() -> None:
    constraints = TransformationConstraints(
        deadline="2026-10-18T00:00:00Z",
        budget_ref="budget:task-001",
        data_classification="confidential",
        resource_refs=("resource:ledger",),
    )
    assert constraints.as_payload() == {
        "deadline": "2026-10-18T00:00:00Z",
        "budget_ref": "budget:task-001",
        "data_classification": "confidential",
        "resource_refs": ["resource:ledger"],
    }
