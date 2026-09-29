"""Pure lifecycle helpers.

The SDK interprets server state; it never performs local lifecycle transitions.
"""

from __future__ import annotations

from typing import Final

from .contracts import ApprovalState, ExecutionState

RUN_TERMINAL_STATES: Final[frozenset[str]] = frozenset({"succeeded", "failed", "cancelled"})
APPROVAL_TERMINAL_STATES: Final[frozenset[str]] = frozenset(
    {"rejected", "expired", "cancelled", "consumed"}
)
EXECUTION_TERMINAL_STATES: Final[frozenset[str]] = frozenset(
    {
        "completed",
        "failed",
        "timed_out",
        "cancelled",
        "denied",
        "budget_exceeded",
        "outcome_unknown",
    }
)


def is_run_terminal(state: str) -> bool:
    return state in RUN_TERMINAL_STATES


def is_approval_terminal(state: str) -> bool:
    return state in APPROVAL_TERMINAL_STATES


def is_execution_terminal(state: str) -> bool:
    return state in EXECUTION_TERMINAL_STATES


def execution_is_retryable(state: ExecutionState, retryable: bool) -> bool:
    return retryable and state != "outcome_unknown"


def validate_execution_state(state: str) -> ExecutionState:
    if state not in {
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
    }:
        raise ValueError("Platform returned an invalid execution state")
    return state  # type: ignore[return-value]


def validate_approval_state(state: str) -> ApprovalState:
    if state not in {"pending", "approved", "rejected", "expired", "cancelled", "consumed"}:
        raise ValueError("Platform returned an invalid approval state")
    return state  # type: ignore[return-value]
