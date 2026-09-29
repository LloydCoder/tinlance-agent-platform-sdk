"""Async facade for the synchronous Platform client.

The facade deliberately reuses the synchronous, audited transport so the two
clients cannot silently diverge in authentication, idempotency, or validation.
"""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

from .client import AgentPlatform
from .config import ClientConfig
from .models import (
    Agent,
    ApprovalDecision,
    ApprovalRef,
    Capability,
    Event,
    EvidenceRef,
    Execution,
    Health,
    Principal,
    Run,
)
from .tools import ToolInvocation


class _AsyncPrincipal:
    def __init__(self, client: AsyncAgentPlatform) -> None:
        self._client = client

    async def get(self, *, request_id: str | None = None) -> Principal:
        return await asyncio.to_thread(self._client._sync.principal.get, request_id=request_id)


class _AsyncAgents:
    def __init__(self, client: AsyncAgentPlatform) -> None:
        self._client = client

    async def list(self, *, request_id: str | None = None) -> tuple[Agent, ...]:
        return await asyncio.to_thread(self._client._sync.agents.list, request_id=request_id)


class _AsyncCapabilities:
    def __init__(self, client: AsyncAgentPlatform) -> None:
        self._client = client

    async def list(
        self, agent_id: UUID | str, *, request_id: str | None = None
    ) -> tuple[Capability, ...]:
        return await asyncio.to_thread(
            self._client._sync.capabilities.list, agent_id, request_id=request_id
        )


class _AsyncRuns:
    def __init__(self, client: AsyncAgentPlatform) -> None:
        self._client = client

    async def create(
        self,
        task_id: UUID | str,
        agent_id: UUID | str,
        intent: str,
        *,
        request_id: str | None = None,
    ) -> Run:
        return await asyncio.to_thread(
            self._client._sync.runs.create,
            task_id,
            agent_id,
            intent,
            request_id=request_id,
        )

    async def cancel(self, run_id: UUID | str, *, request_id: str | None = None) -> Run:
        return await asyncio.to_thread(
            self._client._sync.runs.cancel, run_id, request_id=request_id
        )

    async def events(
        self, run_id: UUID | str, *, request_id: str | None = None
    ) -> tuple[Event, ...]:
        return await asyncio.to_thread(
            self._client._sync.runs.events, run_id, request_id=request_id
        )

    async def evidence(
        self, run_id: UUID | str, *, request_id: str | None = None
    ) -> tuple[EvidenceRef, ...]:
        return await asyncio.to_thread(
            self._client._sync.runs.evidence, run_id, request_id=request_id
        )


class _AsyncApprovals:
    def __init__(self, client: AsyncAgentPlatform) -> None:
        self._client = client

    async def request(
        self,
        run_id: UUID | str,
        action: str,
        resource: str,
        reason: str,
        *,
        intent_fingerprint: str | None = None,
        request_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> ApprovalRef:
        return await asyncio.to_thread(
            self._client._sync.approvals.request,
            run_id,
            action,
            resource,
            reason,
            intent_fingerprint=intent_fingerprint,
            request_id=request_id,
            idempotency_key=idempotency_key,
        )

    async def decide(
        self,
        approval_id: UUID | str,
        approved: bool,
        *,
        intent_fingerprint: str | None = None,
        request_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> ApprovalDecision:
        return await asyncio.to_thread(
            self._client._sync.approvals.decide,
            approval_id,
            approved,
            intent_fingerprint=intent_fingerprint,
            request_id=request_id,
            idempotency_key=idempotency_key,
        )


class _AsyncExecutions:
    def __init__(self, client: AsyncAgentPlatform) -> None:
        self._client = client

    async def get(self, execution_id: UUID | str, *, request_id: str | None = None) -> Execution:
        return await asyncio.to_thread(
            self._client._sync.executions.get,
            execution_id,
            request_id=request_id,
        )


class _AsyncTools:
    def __init__(self, client: AsyncAgentPlatform) -> None:
        self._client = client

    async def execute(
        self,
        run_id: UUID | str,
        agent_id: UUID | str,
        invocation: ToolInvocation,
        **kwargs: Any,
    ) -> Execution:
        return await asyncio.to_thread(
            self._client._sync.tools.execute,
            run_id,
            agent_id,
            invocation,
            **kwargs,
        )


class AsyncAgentPlatform:
    """Async facade preserving the exact Platform v1.1 contract."""

    def __init__(self, config: ClientConfig | None = None, **kwargs: Any) -> None:
        if config is not None:
            self._sync = AgentPlatform(**config.as_client_kwargs())
        else:
            self._sync = AgentPlatform(**kwargs)
        self.principal = _AsyncPrincipal(self)
        self.agents = _AsyncAgents(self)
        self.capabilities = _AsyncCapabilities(self)
        self.runs = _AsyncRuns(self)
        self.approvals = _AsyncApprovals(self)
        self.executions = _AsyncExecutions(self)
        self.tools = _AsyncTools(self)

    async def health(self, *, request_id: str | None = None) -> Health:
        return await asyncio.to_thread(self._sync.health, request_id=request_id)

    async def close(self) -> None:
        """Release the facade; the standard-library transport has no pooled session."""
        await asyncio.sleep(0)
