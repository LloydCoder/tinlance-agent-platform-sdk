"""Minimal agent scaffolding over the governed Platform client.

An AgentScaffold owns no identity or authority. The supplied agent_id is an
opaque Platform-issued identifier and all execution remains server-governed.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from .client import AgentPlatform
from .contracts import CapabilityDeclaration
from .models import Run


@dataclass(frozen=True, slots=True)
class AgentSpec:
    name: str
    version: str
    description: str
    capabilities: tuple[CapabilityDeclaration, ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.version.strip() or not self.description.strip():
            raise ValueError("agent spec requires name, version, and description")


class AgentScaffold:
    """Small composition helper for starting Platform-governed runs."""

    def __init__(
        self,
        client: AgentPlatform,
        *,
        agent_id: UUID,
        task_id: UUID,
        spec: AgentSpec,
    ) -> None:
        self._client = client
        self.agent_id = agent_id
        self.task_id = task_id
        self.spec = spec

    def start(self, intent: str, *, request_id: str | None = None) -> Run:
        if not intent.strip():
            raise ValueError("agent intent is required")
        return self._client.runs.create(
            self.task_id,
            self.agent_id,
            intent,
            request_id=request_id,
        )
