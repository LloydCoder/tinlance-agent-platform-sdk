"""Governed research-agent composition over the existing Platform contract."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from .client import AgentPlatform
from .models import Run


@dataclass(frozen=True, slots=True)
class ResearchRequest:
    objective: str
    task_id: UUID
    agent_id: UUID
    request_id: str | None = None

    def __post_init__(self) -> None:
        if not self.objective.strip():
            raise ValueError("research objective is required")


@dataclass(frozen=True, slots=True)
class ResearchRun:
    request: ResearchRequest
    run: Run


class ResearchAgent:
    """Starts governed research runs; it never bypasses Platform execution authority.

    The current Platform API does not expose a run-get/wait or model/tool endpoint,
    so this class intentionally provides start-only composition rather than fake
    polling or local autonomous execution.
    """

    def __init__(self, client: AgentPlatform) -> None:
        self._client = client

    def start(self, request: ResearchRequest) -> ResearchRun:
        run = self._client.runs.create(
            request.task_id,
            request.agent_id,
            f"research:{request.objective}",
            request_id=request.request_id or str(uuid4()),
        )
        return ResearchRun(request, run)
