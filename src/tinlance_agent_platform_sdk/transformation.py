"""Authority-neutral Transformation contract for P1.

A Transformation records attributable intent, context, governance, execution,
evidence, provenance and business outcomes. It is never an authorization grant.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any, Literal
from uuid import UUID

TransformationExecutionState = Literal[
    "planned", "running", "succeeded", "failed", "cancelled", "partial"
]
TransformationOutcomeStatus = Literal[
    "unknown", "achieved", "partially_achieved", "not_achieved", "inconclusive"
]
TransformationDataClassification = Literal["public", "internal", "confidential", "restricted"]


def _require_normalized(value: str, label: str) -> None:
    if not value or value != value.strip():
        raise ValueError(f"{label} must be non-empty and normalized")


def _validate_datetime(value: str, label: str) -> None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"{label} must be an ISO-8601 date-time") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{label} must include a timezone")


@dataclass(frozen=True, slots=True)
class TransformationMetric:
    name: str
    value: float | int | str | bool
    unit: str | None = None

    def __post_init__(self) -> None:
        _require_normalized(self.name, "transformation metric name")

    def as_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"name": self.name, "value": self.value}
        if self.unit is not None:
            payload["unit"] = self.unit
        return payload


@dataclass(frozen=True, slots=True)
class TransformationReference:
    ref: str
    kind: str
    digest: str | None = None

    def __post_init__(self) -> None:
        _require_normalized(self.ref, "transformation reference")
        _require_normalized(self.kind, "transformation reference kind")
        if self.digest is not None and (
            len(self.digest) != 64 or any(c not in "0123456789abcdef" for c in self.digest)
        ):
            raise ValueError("transformation reference digest must be lowercase SHA-256 hex")

    def as_payload(self) -> dict[str, str]:
        payload = {"ref": self.ref, "kind": self.kind}
        if self.digest is not None:
            payload["digest"] = self.digest
        return payload


@dataclass(frozen=True, slots=True)
class TransformationConstraints:
    deadline: str | None = None
    budget_ref: str | None = None
    data_classification: TransformationDataClassification | None = None
    resource_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.deadline is not None:
            _validate_datetime(self.deadline, "deadline")
        if self.budget_ref is not None:
            _require_normalized(self.budget_ref, "budget_ref")
        if self.data_classification not in (
            None, "public", "internal", "confidential", "restricted"
        ):
            raise ValueError("unsupported transformation data classification")
        if any(not ref.strip() for ref in self.resource_refs):
            raise ValueError("resource references must be non-empty")

    def as_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.deadline is not None:
            payload["deadline"] = self.deadline
        if self.budget_ref is not None:
            payload["budget_ref"] = self.budget_ref
        if self.data_classification is not None:
            payload["data_classification"] = self.data_classification
        if self.resource_refs:
            payload["resource_refs"] = list(self.resource_refs)
        return payload


@dataclass(frozen=True, slots=True)
class TransformationProvenance:
    declared_by: str
    recorded_at: str
    source_refs: tuple[str, ...] = ()
    content_digest: str | None = None

    def __post_init__(self) -> None:
        _require_normalized(self.declared_by, "provenance.declared_by")
        _validate_datetime(self.recorded_at, "provenance.recorded_at")
        if any(not ref.strip() for ref in self.source_refs):
            raise ValueError("provenance source references must be non-empty")
        if self.content_digest is not None and (
            len(self.content_digest) != 64
            or any(c not in "0123456789abcdef" for c in self.content_digest)
        ):
            raise ValueError("provenance content_digest must be lowercase SHA-256 hex")

    def as_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "declared_by": self.declared_by,
            "recorded_at": self.recorded_at,
            "source_refs": list(self.source_refs),
        }
        if self.content_digest is not None:
            payload["content_digest"] = self.content_digest
        return payload


@dataclass(frozen=True, slots=True)
class TransformationOutcome:
    status: TransformationOutcomeStatus
    achieved: bool
    metrics: tuple[TransformationMetric, ...] = ()
    business_effect_refs: tuple[str, ...] = ()
    failure_code: str | None = None

    def __post_init__(self) -> None:
        if self.status == "achieved" and not self.achieved:
            raise ValueError("achieved status requires achieved=true")
        if self.achieved and self.status != "achieved":
            raise ValueError("achieved=true requires achieved status")
        if any(not ref.strip() for ref in self.business_effect_refs):
            raise ValueError("business effect references must be non-empty")
        if self.failure_code is not None:
            _require_normalized(self.failure_code, "failure_code")

    def as_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "achieved": self.achieved,
            "metrics": [metric.as_payload() for metric in self.metrics],
            "business_effect_refs": list(self.business_effect_refs),
        }
        if self.failure_code is not None:
            payload["failure_code"] = self.failure_code
        return payload


@dataclass(frozen=True, slots=True)
class Transformation:
    transformation_id: UUID
    tenant_ref: str
    version: int
    objective: str
    success_criteria: tuple[str, ...]
    principal_ref: str
    agent_ref: str
    agent_version: str
    workspace_ref: str
    task_ref: str
    requested_capabilities: tuple[tuple[str, str], ...]
    policy_refs: tuple[str, ...]
    risk_class: str
    idempotency_key: str
    execution_state: TransformationExecutionState = "planned"
    run_ref: str | None = None
    output_refs: tuple[TransformationReference, ...] = ()
    evidence_refs: tuple[TransformationReference, ...] = ()
    outcome: TransformationOutcome | None = None
    schema_version: str = "transformation/v1"
    business_metric: str | None = None
    delegated_by: str | None = None
    source_refs: tuple[str, ...] = ()
    approval_refs: tuple[str, ...] = ()
    deadline: str | None = None
    budget_ref: str | None = None
    data_classification: TransformationDataClassification | None = None
    resource_refs: tuple[str, ...] = ()
    started_at: str | None = None
    completed_at: str | None = None
    provenance: TransformationProvenance = field(
        default_factory=lambda: TransformationProvenance(
            declared_by="tinlance-agent-platform-sdk",
            recorded_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        )
    )

    def __post_init__(self) -> None:
        if self.schema_version != "transformation/v1":
            raise ValueError("unsupported transformation schema version")
        if self.version < 1:
            raise ValueError("transformation version must be >= 1")
        for value, label in (
            (self.tenant_ref, "tenant_ref"),
            (self.objective, "objective"),
            (self.principal_ref, "principal_ref"),
            (self.agent_ref, "agent_ref"),
            (self.agent_version, "agent_version"),
            (self.workspace_ref, "workspace_ref"),
            (self.task_ref, "task_ref"),
            (self.risk_class, "risk_class"),
            (self.idempotency_key, "idempotency_key"),
        ):
            _require_normalized(value, label)
        if not 16 <= len(self.idempotency_key) <= 256:
            raise ValueError("transformation idempotency key must contain 16 to 256 characters")
        if not self.success_criteria or any(not item.strip() for item in self.success_criteria):
            raise ValueError("transformation requires non-empty success criteria")
        if not self.requested_capabilities:
            raise ValueError("transformation requires at least one requested capability")
        if not self.policy_refs or any(not ref.strip() for ref in self.policy_refs):
            raise ValueError("transformation requires at least one policy reference")
        if any(
            not ref.strip() or not reason.strip() for ref, reason in self.requested_capabilities
        ):
            raise ValueError("requested capabilities require a reference and reason")
        if any(
            not ref.strip() for ref in self.approval_refs + self.source_refs + self.resource_refs
        ):
            raise ValueError("transformation references must be non-empty")
        if self.business_metric is not None:
            _require_normalized(self.business_metric, "business_metric")
        if self.delegated_by is not None:
            _require_normalized(self.delegated_by, "delegated_by")
        if self.run_ref is not None:
            _require_normalized(self.run_ref, "run_ref")
        if self.deadline is not None:
            _validate_datetime(self.deadline, "deadline")
        if self.budget_ref is not None:
            _require_normalized(self.budget_ref, "budget_ref")
        if self.data_classification not in (
            None, "public", "internal", "confidential", "restricted"
        ):
            raise ValueError("unsupported transformation data classification")
        if self.started_at is not None:
            _validate_datetime(self.started_at, "started_at")
        if self.completed_at is not None:
            _validate_datetime(self.completed_at, "completed_at")
        if self.completed_at is not None and self.started_at is None:
            raise ValueError("completed_at requires started_at")

    def as_payload(self) -> dict[str, Any]:
        intent: dict[str, Any] = {
            "objective": self.objective,
            "success_criteria": list(self.success_criteria),
        }
        if self.business_metric is not None:
            intent["business_metric"] = self.business_metric
        actor: dict[str, Any] = {
            "principal_ref": self.principal_ref,
            "agent_ref": self.agent_ref,
            "agent_version": self.agent_version,
        }
        if self.delegated_by is not None:
            actor["delegated_by"] = self.delegated_by
        context: dict[str, Any] = {"workspace_ref": self.workspace_ref, "task_ref": self.task_ref}
        if self.source_refs:
            context["source_refs"] = list(self.source_refs)
        constraints = TransformationConstraints(
            deadline=self.deadline,
            budget_ref=self.budget_ref,
            data_classification=self.data_classification,
            resource_refs=self.resource_refs,
        ).as_payload()
        governance: dict[str, Any] = {
            "policy_refs": list(self.policy_refs),
            "risk_class": self.risk_class,
        }
        if self.approval_refs:
            governance["approval_refs"] = list(self.approval_refs)
        execution: dict[str, Any] = {
            "state": self.execution_state,
            "idempotency_key": self.idempotency_key,
        }
        if self.run_ref is not None:
            execution["run_ref"] = self.run_ref
        if self.started_at is not None:
            execution["started_at"] = self.started_at
        if self.completed_at is not None:
            execution["completed_at"] = self.completed_at
        return {
            "schema_version": self.schema_version,
            "transformation_id": str(self.transformation_id),
            "version": self.version,
            "tenant_ref": self.tenant_ref,
            "intent": intent,
            "actor": actor,
            "context": context,
            "requested_capabilities": [
                {"capability_ref": ref, "reason": reason}
                for ref, reason in self.requested_capabilities
            ],
            "constraints": constraints,
            "governance": governance,
            "execution": execution,
            "outputs": [ref.as_payload() for ref in self.output_refs],
            "evidence": [ref.as_payload() for ref in self.evidence_refs],
            "outcome": self.outcome.as_payload()
            if self.outcome is not None
            else {
                "status": "unknown",
                "achieved": False,
                "metrics": [],
                "business_effect_refs": [],
            },
            "provenance": self.provenance.as_payload(),
        }

    def content_digest(self) -> str:
        payload = self.as_payload()
        payload["provenance"] = dict(payload["provenance"])
        payload["provenance"].pop("content_digest", None)
        encoded = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        return sha256(encoded).hexdigest()
