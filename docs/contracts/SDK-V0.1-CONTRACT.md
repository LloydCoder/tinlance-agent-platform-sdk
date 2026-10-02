# Tinlance Agent Platform SDK v0.1 Historical Contract

> Superseded by `docs/contracts/SDK-V1.0-CONTRACT.md`. Retained as the forensic v0.1 baseline; it is not the current public contract.

**SDK:** 0.1.0  
**Platform API:** 1.1  
**Governed execution contract:** `governed-execution.v1`  
**Endpoint:** `POST /v1/agent-platform`  
**Status:** implementation contract

## Authority

The SDK implements only the executable Platform API v1.1 operation surface established by the Tinlance Agent Platform repository.

The external SDK is independent of Platform implementation packages. The Platform remains the authority for authentication, authorization, policy, approvals, tool permissions, secrets, sandboxing, evidence and execution.

## Wire request

```json
{
  "tenant_id": "tenant-a",
  "subject_id": "user-a",
  "operation": "health",
  "payload": {}
}
```

Required headers:

- `Content-Type: application/json`
- `Authorization: Bearer <credential>`
- `X-Tinlance-API-Version: 1.1`
- `X-Request-ID: <normalized request id>`

Optional:

- `Idempotency-Key` — independent idempotency key for consequential operations; it is scoped to the authenticated tenant and request fingerprint
- `traceparent` — strict W3C Trace Context value

The request body is JSON and the current Platform boundary limits it to 1 MiB.

The SDK additionally requires HTTPS by default. Explicit `allow_insecure_http=True` is available for controlled local/test environments only.

## Response

Success:

```json
{"status":"ok","payload":{}}
```

or, for consequential operations:

```json
{"status":"accepted","payload":{}}
```

HTTP success is currently 200 for both.

Error:

```json
{"error":"error_code"}
```

Responses must advertise `X-Tinlance-API-Version: 1.1` and use `Content-Type: application/json` (optional media-type parameters are allowed). The SDK rejects mismatches. SDK response bodies are bounded by a configurable limit (8 MiB by default).

Stable mappings are 400 `invalid_request`, 401 `unauthorized`, 403 `forbidden`, 409 `idempotency_conflict`, 413 `request_too_large`, 415 `json_required`, 426 `api_version_required`, and 500 `platform_error`.

## Public operations

| SDK method | Operation | Consequential |
| --- | --- | --- |
| `health()` | `health` | no |
| `principal.get()` | `principal.get` | no |
| `agents.list()` | `agents.list` | no |
| `capabilities.list(agent_id)` | `capabilities.list` | no |
| `runs.create(task_id, agent_id, intent)` | `runs.create` | yes |
| `runs.cancel(run_id)` | `runs.cancel` | yes |
| `approvals.request(run_id, action, resource, reason)` | `approvals.request` | yes |
| `approvals.decide(approval_id, approved)` | `approvals.decide` | yes |
| `tools.execute(run_id, agent_id, invocation, ...)` | `tools.execute` | yes |
| `executions.get(execution_id)` | `executions.get` | no |
| `runs.events(run_id)` | `runs.events` | no |
| `runs.evidence(run_id)` | `runs.evidence` | no |

No other remote operation is exposed by SDK v0.1.

## Idempotency

The Platform guards `runs.create`, `runs.cancel`, `approvals.request`, `approvals.decide`, and `tools.execute`. R10 execution uses a distinct idempotency key from the request ID when the caller supplies one; the server fingerprints security-relevant execution intent and rejects conflicting reuse.

For a caller-supplied request ID, a retry must reuse the same request ID. The SDK does not automatically retry consequential requests because the reference Platform's idempotency store is bounded in-memory state rather than a distributed exactly-once guarantee.

A reused request ID with a different consequential request produces HTTP 409.

## Models

The SDK exposes typed immutable models for the currently public response contracts.

Run states:

```
created
running
waiting_approval
succeeded
failed
cancelled
```

Approval states:

```
pending
approved
rejected
expired
cancelled
consumed
```

R10 execution states include `requested`, `waiting_approval`, `authorized`, `running`, `completed`, `failed`, `timed_out`, `cancelled`, `denied`, `budget_exceeded`, and `outcome_unknown`.

The SDK represents these values; it does not transition them locally.

## Explicit exclusions

Until the Platform publishes corresponding versioned operations, SDK v0.1 does not implement:

- `runs.get`
- `runs.wait`
- approval get/approve/reject/cancel
- `tools.list`
- event streaming
- evidence content retrieval
- pagination
- webhook subscriptions
- OpenAPI-generated resource clients

## Compatibility

SDK package version and Platform API version are independent.

- SDK: `0.1.0`
- Platform API: `1.1`
- Python: 3.12–3.14

A future API version must be introduced by the Platform contract first. The SDK must not infer or emulate server capabilities.

## Source-of-truth hierarchy

1. Current executable Platform implementation.
2. Current executable Platform API/conformance tests.
3. Server-side SDK v0.1 forensic contract.
4. This repository's SDK contract and tests.
5. Architecture and roadmap documentation.
6. Historical planning material.

If a discrepancy appears, implementation must follow the server contract rather than an SDK-side assumption.

## M0 security foundation

SDK M0 is documented and enforced in [docs/M0.md](../M0.md). The M0 boundary is fail-closed for HTTPS, redirects, response API version, response media type, response size, and operation-specific success status. No additional remote operations are introduced.
