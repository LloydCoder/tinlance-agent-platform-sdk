"""Typed tool contracts for SDK consumers.

These are data contracts only. Tool authorization and execution remain Platform
authority. No local executor can use these types to grant itself permission.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ToolDescriptor:
    name: str
    capability: str
    description: str
    version: str = "1"


@dataclass(frozen=True, slots=True)
class ToolInvocation:
    tool_name: str
    capability: str
    action: str
    resource: str
    arguments: dict[str, Any]

    def __post_init__(self) -> None:
        if not self.tool_name.strip() or not self.capability.strip():
            raise ValueError("tool_name and capability are required")
        if not self.action.strip() or not self.resource.strip():
            raise ValueError("action and resource are required")
        if not isinstance(self.arguments, dict):
            raise ValueError("arguments must be an object")


@dataclass(frozen=True, slots=True)
class ToolResult:
    tool_name: str
    output: str
    evidence_id: str | None = None


class ToolContractRegistry:
    """Local metadata registry; it never authorizes or executes a tool."""

    def __init__(self) -> None:
        self._items: dict[str, ToolDescriptor] = {}

    def register(self, descriptor: ToolDescriptor) -> None:
        if not descriptor.name.strip() or not descriptor.capability.strip():
            raise ValueError("tool descriptor requires name and capability")
        if descriptor.name in self._items:
            raise ValueError("tool descriptor is immutable")
        self._items[descriptor.name] = descriptor

    def get(self, name: str) -> ToolDescriptor:
        return self._items[name]

    def list(self) -> tuple[ToolDescriptor, ...]:
        return tuple(self._items[name] for name in sorted(self._items))
