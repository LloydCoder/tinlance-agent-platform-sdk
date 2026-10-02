"""Contract-gated optional SDK capabilities.

These declarations are intentionally descriptive. A capability becomes public
only after the Platform publishes a versioned contract and executable
conformance tests.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DeferredCapability:
    name: str
    required_platform_contract: str
    reason: str


STREAMING = DeferredCapability(
    name="events.stream",
    required_platform_contract="platform.events.stream.v1",
    reason="No authoritative Platform streaming contract is published yet.",
)
PAGINATION = DeferredCapability(
    name="pagination",
    required_platform_contract="platform.pagination.v1",
    reason="No authoritative Platform pagination contract is published yet.",
)
WEBHOOKS = DeferredCapability(
    name="webhooks",
    required_platform_contract="platform.webhooks.v1",
    reason="No authoritative Platform webhook contract is published yet.",
)


def deferred_capabilities() -> tuple[DeferredCapability, ...]:
    """Return immutable, explicit future-capability declarations."""
    return (STREAMING, PAGINATION, WEBHOOKS)
