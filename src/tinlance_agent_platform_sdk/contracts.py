"""Typed, authority-neutral developer contracts for R10.

These declarations describe intent and transport data. They never grant capability,
approve an action, authorize a principal, execute a tool, or validate server policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Literal
from uuid import UUID

GOVERNED_EXECUTION_CONTRACT = "governed-execution.v1"

ExecutionState = Literal[
    "requested",
    "waiting_approval",
    "authorized",
    "running",
    "completed",
    "failed",
    "timed_out",
    "cancelled",
    "denied",
    "budget_exceeded",
    "outcome_unknown",
]

ApprovalState = Literal["pending", "approved", "rejected", "expired", "cancelled", "consumed"]


def canonical_intent_fingerprint(payload: dict[str, Any]) -> str:
    """Return a deterministic client-side fingerprint for correlation only.

    The Platform remains authoritative and recomputes its own security fingerprint.
    """
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )
    return sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class CapabilityDeclaration:
    """Declarative metadata; not an authorization grant."""

    capability_id: str
    version: str
    description: str
    scopes: tuple[str, ...] = ()
    tool_names: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.capability_id.strip() or not self.version.strip() or not self.description.strip():
            raise ValueError("capability declaration requires id, version, and description")
        if any(not item.strip() for item in self.scopes + self.tool_names):
            raise ValueError("capability declaration entries must be non-empty")

    def as_payload(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "version": self.version,
            "description": self.description,
            "scopes": list(self.scopes),
            "tool_names": list(self.tool_names),
        }


@dataclass(frozen=True, slots=True)
class ApprovalRequest:
    run_id: UUID
    action: str
    resource: str
    reason: str
    intent_fingerprint: str | None = None

    def as_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "run_id": str(self.run_id),
            "action": self.action,
            "resource": self.resource,
            "reason": self.reason,
        }
        if self.intent_fingerprint is not None:
            payload["intent_fingerprint"] = self.intent_fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class EvidenceReference:
    evidence_id: UUID
    execution_id: UUID | None = None

    def as_payload(self) -> dict[str, str]:
        payload = {"evidence_id": str(self.evidence_id)}
        if self.execution_id is not None:
            payload["execution_id"] = str(self.execution_id)
        return payload


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    execution_id: UUID
    state: ExecutionState
    output: str | None
    evidence: tuple[EvidenceReference, ...]
    audit_event_ids: tuple[UUID, ...]
    error_code: str | None
    retryable: bool

    @property
    def terminal(self) -> bool:
        return self.state in {
            "completed",
            "failed",
            "timed_out",
            "cancelled",
            "denied",
            "budget_exceeded",
            "outcome_unknown",
        }

    @property
    def outcome_unknown(self) -> bool:
        return self.state == "outcome_unknown"

    @property
    def safe_to_retry(self) -> bool:
        return self.retryable and not self.outcome_unknown


@dataclass(frozen=True, slots=True)
class StructuredError:
    code: str
    message: str
    status_code: int | None = None
    request_id: str | None = None
    operation: str | None = None
    retryable: bool = False

    def __post_init__(self) -> None:
        if not self.code.strip() or not self.message.strip():
            raise ValueError("structured errors require code and message")
