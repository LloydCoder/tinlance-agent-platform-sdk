"""Approval workflow composition without local approval authority."""

from __future__ import annotations

from uuid import UUID

from .client import AgentPlatform
from .contracts import ApprovalRequest
from .models import ApprovalDecision, ApprovalRef


class ApprovalWorkflow:
    """Transport-only approval workflow facade.

    It never decides whether an action is approvable and never changes approval state
    locally; the Platform remains the authority.
    """

    def __init__(self, client: AgentPlatform) -> None:
        self._client = client

    def request(
        self,
        request: ApprovalRequest,
        *,
        request_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> ApprovalRef:
        return self._client.approvals.request(
            request.run_id,
            request.action,
            request.resource,
            request.reason,
            intent_fingerprint=request.intent_fingerprint,
            request_id=request_id,
            idempotency_key=idempotency_key,
        )

    def decide(
        self,
        approval_id: UUID,
        approved: bool,
        *,
        intent_fingerprint: str | None = None,
        request_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> ApprovalDecision:
        return self._client.approvals.decide(
            approval_id,
            approved,
            intent_fingerprint=intent_fingerprint,
            request_id=request_id,
            idempotency_key=idempotency_key,
        )
