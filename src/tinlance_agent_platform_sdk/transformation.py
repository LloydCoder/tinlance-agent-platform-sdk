"""Authority-neutral Transformation contract for P1.

A Transformation records intent, context, governance references, execution,
evidence, and business outcome. It is data, not an authorization grant.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Literal
from uuid import UUID

TransformationExecutionState = Literal[
    "planned", "running", "succeeded", "failed", "cancelled", "partial"
]
TransformationOutcomeStatus = Literal[
    "unknown", "achieved", "partially_achieved", "not_achieved", "inconclusive"
]


@dataclass(frozen=True, slots=True)
class TransformationMetric:
    name: str
    value: float | int | str | bool
    unit: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("transformation metric name is required")


@dataclass(frozen=True, slots=True)
class TransformationReference:
    ref: str
    kind: str
    digest: str | None = None

    def __post_init__(self) -> None:
        if not self.ref.strip() or not self.kind.strip():
            raise ValueError("transformation references require ref and kind")
        if self.digest is not None and (
            len(self.digest) != 64 or any(c not in "0123456789abcdef" for c in self.digest)
        ):
            raise ValueError("transformation reference digest must be a lowercase SHA-256 hex digest")

    def as_payload(self) -> dict[str, str]:
        payload = {"ref": self.ref, "kind": self.kind}
        if self.digest is not None:
            payload["digest"] = self.digest
        return payload


@dataclass(frozen=True, slots=True)
class TransformationOutcome:
    status: TransformationOutcomeStatus
    achieved: bool
    metrics: tuple[TransformationMetric, ...] = ()
    business_effect_refs: tuple[str, ...] = ()
    failure_code: str | None = None

    def as_payload(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "achieved": self.achieved,
            "metrics": [
                {"name": m.name, "value": m.value, **({"unit": m.unit} if m.unit else {})}
                for m in self.metrics
            ],
            "business_effect_refs": list(self.business_effect_refs),
            **({"failure_code": self.failure_code} if self.failure_code else {}),
        }


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

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError("transformation version must be >= 1")
        for value in (
            self.tenant_ref,
            self.objective,
            self.principal_ref,
            self.agent_ref,
            self.agent_version,
            self.workspace_ref,
            self.task_ref,
            self.idempotency_key,
        ):
            if not value.strip():
                raise ValueError("transformation identifiers and objective must be non-empty")
        if len(self.idempotency_key) < 16:
            raise ValueError("transformation idempotency key is too short")
        if not self.success_criteria or any(not item.strip() for item in self.success_criteria):
            raise ValueError("transformation requires non-empty success criteria")
        if not self.requested_capabilities:
            raise ValueError("transformation requires at least one requested capability")
        if not self.policy_refs:
            raise ValueError("transformation requires at least one policy reference")

    def as_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "transformation_id": str(self.transformation_id),
            "version": self.version,
            "tenant_ref": self.tenant_ref,
            "intent": {
                "objective": self.objective,
                "success_criteria": list(self.success_criteria),
            },
            "actor": {
                "principal_ref": self.principal_ref,
                "agent_ref": self.agent_ref,
                "agent_version": self.agent_version,
            },
            "context": {"workspace_ref": self.workspace_ref, "task_ref": self.task_ref},
            "requested_capabilities": [
                {"capability_ref": ref, "reason": reason}
                for ref, reason in self.requested_capabilities
            ],
            "constraints": {},
            "governance": {
                "policy_refs": list(self.policy_refs),
                "risk_class": self.risk_class,
            },
            "execution": {
                "state": self.execution_state,
                "idempotency_key": self.idempotency_key,
                **({"run_ref": self.run_ref} if self.run_ref else {}),
            },
            "outputs": [ref.as_payload() for ref in self.output_refs],
            "evidence": [ref.as_payload() for ref in self.evidence_refs],
            "outcome": self.outcome.as_payload()
            if self.outcome is not None
            else {"status": "unknown", "achieved": False, "metrics": [], "business_effect_refs": []},
        }

    def content_digest(self) -> str:
        encoded = json.dumps(
            self.as_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        return sha256(encoded).hexdigest()
