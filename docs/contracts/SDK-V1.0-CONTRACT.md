# Tinlance Agent Platform SDK v1.0 Contract

**Status:** Stable external SDK contract  
**SDK:** 1.0.0  
**Platform API:** 1.1

## Authority

The SDK is a thin consumer-side contract/client layer. The Platform remains
authoritative for identity, tenant binding, authorization, policy, approvals,
tool permissions, secrets, sandboxing, execution, evidence validity and audit.

## Public wire surface

The SDK communicates through:

`POST /v1/agent-platform`

with:

- `Content-Type: application/json`
- `Authorization: Bearer <opaque credential>`
- `X-Tinlance-API-Version: 1.1`
- `X-Request-ID`
- optional `Idempotency-Key`
- optional W3C `traceparent`/`tracestate`

The public operation set is the machine-readable
`docs/contracts/sdk-contract-manifest.json`.

## Compatibility

SDK 1.0 supports Platform API 1.1 and Python 3.12–3.14. The SDK fails closed
when configured for an unsupported Platform API version.

## Stability rules

- patch releases preserve the public API;
- minor releases add only backward-compatible surfaces;
- breaking SDK changes require a new major version;
- new Platform operations require an explicit versioned Platform contract and
  executable conformance tests before SDK exposure.

## Deferred protocol surfaces

Streaming, pagination, webhooks, evidence-content retrieval and resource-oriented
REST endpoints remain contract-gated because Platform API 1.1 does not publish
those protocols.

## Security

The SDK validates transport and response boundaries, limits response size,
disables authenticated redirects, preserves request/idempotency identity, and
does not export credentials or payloads through its telemetry interface.

## Source of truth

Executable Platform behavior and conformance tests outrank historical
documentation. This contract records the stable external SDK boundary and is
reconciled with the canonical contract manifest.
