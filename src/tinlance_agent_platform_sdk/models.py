"""Typed models for the stable Platform API v1.1 response surface."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


def _text(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Platform returned an invalid {key}")
    return value


def _uuid(value: str) -> UUID:
    try:
        return UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ValueError("Platform returned an invalid UUID") from exc


@dataclass(frozen=True, slots=True)
class Health:
    ready: bool

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> Health:
        value = payload.get("ready")
        if not isinstance(value, bool):
            raise ValueError("Platform returned an invalid health payload")
        return cls(value)


@dataclass(frozen=True, slots=True)
class Principal:
    user_id: str

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> Principal:
        value = payload.get("user_id")
        if not isinstance(value, str) or not value:
            raise ValueError("Platform returned an invalid principal payload")
        return cls(value)


@dataclass(frozen=True, slots=True)
class Agent:
    agent_id: UUID
    name: str
    version: str

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> Agent:
        agent_id = _text(payload, "agent_id")
        name = _text(payload, "name")
        version = _text(payload, "version")
        return cls(_uuid(agent_id), name, version)


@dataclass(frozen=True, slots=True)
class Capability:
    capability_id: str

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> Capability:
        value = payload.get("capability_id")
        if not isinstance(value, str) or not value:
            raise ValueError("Platform returned an invalid capability payload")
        return cls(value)


@dataclass(frozen=True, slots=True)
class Run:
    run_id: UUID
    task_id: UUID
    state: str
    agent_id: UUID

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> Run:
        run_id = _text(payload, "run_id")
        task_id = _text(payload, "task_id")
        state = _text(payload, "state")
        agent_id = _text(payload, "agent_id")
        if state not in RUN_STATES:
            raise ValueError("Platform returned an invalid run state")
        return cls(_uuid(run_id), _uuid(task_id), state, _uuid(agent_id))


@dataclass(frozen=True, slots=True)
class ApprovalRef:
    approval_id: UUID

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> ApprovalRef:
        value = payload.get("approval_id")
        if not isinstance(value, str) or not value:
            raise ValueError("Platform returned an invalid approval payload")
        return cls(_uuid(value))


@dataclass(frozen=True, slots=True)
class Event:
    event_id: UUID
    event_type: str
    occurred_at: datetime
    request_id: str
    correlation_id: str
    workspace_id: str
    task_id: UUID | None
    agent_id: UUID | None
    platform_run_id: UUID
    payload: dict[str, Any]

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> Event:
        values = (
            payload.get("event_id"),
            payload.get("event_type"),
            payload.get("occurred_at"),
            payload.get("request_id"),
            payload.get("correlation_id"),
            payload.get("workspace_id"),
            payload.get("platform_run_id"),
        )
        if not all(isinstance(value, str) and value for value in values):
            raise ValueError("Platform returned an invalid event payload")
        raw_payload = payload.get("payload")
        if not isinstance(raw_payload, dict):
            raise ValueError("Platform returned an invalid event data payload")
        try:
            parsed_time = datetime.fromisoformat(payload["occurred_at"])
        except ValueError as exc:
            raise ValueError("Platform returned an invalid event timestamp") from exc
        if parsed_time.tzinfo is None or parsed_time.utcoffset() is None:
            raise ValueError("Platform returned a timezone-naive event timestamp")
        task_id = payload.get("task_id")
        agent_id = payload.get("agent_id")
        if task_id is not None and not isinstance(task_id, str):
            raise ValueError("Platform returned an invalid task_id")
        if agent_id is not None and not isinstance(agent_id, str):
            raise ValueError("Platform returned an invalid agent_id")
        return cls(
            _uuid(payload["event_id"]),
            payload["event_type"],
            parsed_time,
            payload["request_id"],
            payload["correlation_id"],
            payload["workspace_id"],
            _uuid(task_id) if task_id else None,
            _uuid(agent_id) if agent_id else None,
            _uuid(payload["platform_run_id"]),
            dict(raw_payload),
        )


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    evidence_id: UUID

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> EvidenceRef:
        value = payload.get("evidence_id")
        if not isinstance(value, str) or not value:
            raise ValueError("Platform returned an invalid evidence reference")
        return cls(_uuid(value))


RUN_STATES = frozenset(
    {
        "created",
        "running",
        "waiting_approval",
        "succeeded",
        "failed",
        "cancelled",
    }
)

APPROVAL_STATES = frozenset(
    {
        "pending",
        "approved",
        "rejected",
        "expired",
    }
)


@dataclass(frozen=True, slots=True)
class ApprovalDecision:
    approval_id: UUID
    state: str

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> ApprovalDecision:
        value = payload.get("approval_id")
        state = payload.get("state")
        if not isinstance(value, str) or not isinstance(state, str) or not value or not state:
            raise ValueError("Platform returned an invalid approval decision payload")
        return cls(_uuid(value), state)


@dataclass(frozen=True, slots=True)
class Execution:
    execution_id: UUID
    state: str
    output: str | None
    evidence_ids: tuple[UUID, ...]
    audit_event_ids: tuple[UUID, ...]
    error_code: str | None
    retryable: bool

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> Execution:
        execution_id = _text(payload, "execution_id")
        state = _text(payload, "state")
        output = payload.get("output")
        if output is not None and not isinstance(output, str):
            raise ValueError("Platform returned an invalid execution output")
        evidence = payload.get("evidence_ids", [])
        audit = payload.get("audit_event_ids", [])
        retryable = payload.get("retryable", False)
        error_code = payload.get("error_code")
        if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
            raise ValueError("Platform returned invalid evidence identifiers")
        if not isinstance(audit, list) or not all(isinstance(item, str) for item in audit):
            raise ValueError("Platform returned invalid audit identifiers")
        if not isinstance(retryable, bool):
            raise ValueError("Platform returned invalid retryability")
        if error_code is not None and not isinstance(error_code, str):
            raise ValueError("Platform returned invalid execution error code")
        return cls(
            _uuid(execution_id),
            state,
            output,
            tuple(_uuid(item) for item in evidence),
            tuple(_uuid(item) for item in audit),
            error_code,
            retryable,
        )
