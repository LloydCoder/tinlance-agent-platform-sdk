"""Declarative agent developer contracts over the governed Platform client.

Agent metadata is a developer-side description. It never grants authority,
selects credentials, changes Platform policy, or executes tools locally.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from .client import AgentPlatform
from .contracts import CapabilityDeclaration
from .models import Run
from .tools import ToolDescriptor


@dataclass(frozen=True, slots=True)
class ModelSpec:
    """Provider/model metadata only; credentials and model authority stay server-side."""

    provider: str
    model: str
    version: str | None = None

    def __post_init__(self) -> None:
        if not self.provider.strip() or not self.model.strip():
            raise ValueError("model spec requires provider and model")
        if self.version is not None and not self.version.strip():
            raise ValueError("model version must be non-empty when supplied")

    def as_payload(self) -> dict[str, str]:
        payload = {"provider": self.provider, "model": self.model}
        if self.version is not None:
            payload["version"] = self.version
        return payload


@dataclass(frozen=True, slots=True)
class GuardrailSpec:
    """Declarative guardrail metadata; Platform policy remains authoritative."""

    name: str
    kind: str
    mode: str = "enforce"

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.kind.strip() or not self.mode.strip():
            raise ValueError("guardrail spec requires name, kind, and mode")

    def as_payload(self) -> dict[str, str]:
        return {"name": self.name, "kind": self.kind, "mode": self.mode}


@dataclass(frozen=True, slots=True)
class LifecycleSpec:
    """Developer lifecycle metadata with no remote state-transition authority."""

    restartable: bool = True
    resumable: bool = False
    shutdown_graceful: bool = True

    def as_payload(self) -> dict[str, bool]:
        return {
            "restartable": self.restartable,
            "resumable": self.resumable,
            "shutdown_graceful": self.shutdown_graceful,
        }


@dataclass(frozen=True, slots=True)
class ObservabilitySpec:
    """Safe observability metadata; payload capture is never implied."""

    service_name: str | None = None
    environment: str | None = None
    trace_enabled: bool = True
    attributes: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.service_name is not None and not self.service_name.strip():
            raise ValueError("service_name must be non-empty when supplied")
        if self.environment is not None and not self.environment.strip():
            raise ValueError("environment must be non-empty when supplied")
        if any(not key.strip() or not value.strip() for key, value in self.attributes):
            raise ValueError("observability attributes must contain non-empty strings")

    def as_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"trace_enabled": self.trace_enabled}
        if self.service_name is not None:
            payload["service_name"] = self.service_name
        if self.environment is not None:
            payload["environment"] = self.environment
        if self.attributes:
            payload["attributes"] = dict(self.attributes)
        return payload


@dataclass(frozen=True, slots=True)
class AgentSpec:
    """Complete declarative agent description for local composition and tooling."""

    name: str
    version: str
    description: str
    capabilities: tuple[CapabilityDeclaration, ...] = ()
    instructions: str | None = None
    reference: str | None = None
    tools: tuple[ToolDescriptor, ...] = ()
    model: ModelSpec | None = None
    guardrails: tuple[GuardrailSpec, ...] = ()
    lifecycle: LifecycleSpec = field(default_factory=LifecycleSpec)
    observability: ObservabilitySpec = field(default_factory=ObservabilitySpec)
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.version.strip() or not self.description.strip():
            raise ValueError("agent spec requires name, version, and description")
        if self.instructions is not None and not self.instructions.strip():
            raise ValueError("instructions must be non-empty when supplied")
        if self.reference is not None and not self.reference.strip():
            raise ValueError("reference must be non-empty when supplied")
        if any(not key.strip() or not value.strip() for key, value in self.metadata):
            raise ValueError("agent metadata must contain non-empty strings")

    def as_payload(self) -> dict[str, Any]:
        """Serialize declarative metadata without authority-bearing fields."""
        payload: dict[str, Any] = {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": [item.as_payload() for item in self.capabilities],
            "tools": [
                {
                    "name": item.name,
                    "capability": item.capability,
                    "description": item.description,
                    "version": item.version,
                }
                for item in self.tools
            ],
            "guardrails": [item.as_payload() for item in self.guardrails],
            "lifecycle": self.lifecycle.as_payload(),
            "observability": self.observability.as_payload(),
        }
        if self.instructions is not None:
            payload["instructions"] = self.instructions
        if self.reference is not None:
            payload["reference"] = self.reference
        if self.model is not None:
            payload["model"] = self.model.as_payload()
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        return payload


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
