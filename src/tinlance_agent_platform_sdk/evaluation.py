"""Typed evaluation references without embedding an evaluation engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EvaluationOutcome = Literal["pass", "fail", "unknown", "partial"]


@dataclass(frozen=True, slots=True)
class EvaluationAssertion:
    name: str
    passed: bool | None
    reason_code: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("evaluation assertion name is required")
        if self.reason_code is not None and not self.reason_code.strip():
            raise ValueError("reason code must be non-empty when supplied")


@dataclass(frozen=True, slots=True)
class EvaluationCase:
    case_id: str
    version: str
    name: str
    criteria: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.case_id.strip() or not self.version.strip() or not self.name.strip():
            raise ValueError("evaluation case requires id, version, and name")
        if any(not criterion.strip() for criterion in self.criteria):
            raise ValueError("evaluation criteria must be non-empty")


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    case_id: str
    outcome: EvaluationOutcome
    assertions: tuple[EvaluationAssertion, ...] = ()
    evidence_references: tuple[str, ...] = ()
    trace_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("evaluation result case id is required")
        if any(not reference.strip() for reference in self.evidence_references):
            raise ValueError("evidence references must be non-empty")
        if any(not reference.strip() for reference in self.trace_references):
            raise ValueError("trace references must be non-empty")

    @property
    def passed(self) -> bool | None:
        if self.outcome == "pass":
            return True
        if self.outcome == "fail":
            return False
        return None
