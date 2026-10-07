# P10 — Replication & Agent System GA

The SDK participates in P10 as the typed transport/composition surface between Agent OS/developer applications and Agent Platform.

## Contract

The same SDK contract must work for multiple independent tenants without changing the authority model. Tenant, principal, request, trace, idempotency and execution references remain opaque/typed values governed by Platform.

## Invariants

- SDK methods do not authorize.
- SDK cannot widen a capability, tenant, approval, budget, sandbox or secret scope.
- Replica-specific configuration is data/configuration, never a second policy engine.
- Cross-tenant identifiers are rejected by the authoritative Platform boundary.
- SDK compatibility is pinned to the ecosystem lock.

## Exit gate

P10 is complete for the SDK only when its CI/security gates are green and the replication conformance suite proves identical contract behavior for two independent tenant configurations.
