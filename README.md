# Tinlance Agent Platform SDK

Official developer SDK for building secure, governed AI agents on the Tinlance Agent Platform.

[![CI](https://github.com/LloydCoder/tinlance-agent-platform-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/LloydCoder/tinlance-agent-platform-sdk/actions/workflows/ci.yml)

## Overview

The Tinlance Agent Platform SDK is the external, consumer-facing Python client for the Tinlance Agent Platform's versioned HTTP boundary.

It is deliberately a **thin contract layer**, not a second agent runtime or authority engine. The Platform remains authoritative for identity verification, tenant binding, authorization, policy, approvals, tool permissions, secrets, sandboxing, evidence validity, and execution.

The SDK is independent of the Platform repository and does not import Platform implementation packages.

## v0.1 / Platform API 1.1

SDK 0.1.0 targets the currently implemented Platform API 1.1 operation gateway.

| SDK surface | Platform operation |
| --- | --- |
| `health()` | `health` |
| `principal.get()` | `principal.get` |
| `agents.list()` | `agents.list` |
| `capabilities.list(agent_id)` | `capabilities.list` |
| `runs.create(task_id, agent_id, intent)` | `runs.create` |
| `runs.cancel(run_id)` | `runs.cancel` |
| `approvals.request(run_id, action, resource, reason)` | `approvals.request` |
| `runs.events(run_id)` | `runs.events` |
| `runs.evidence(run_id)` | `runs.evidence` |

The wire endpoint is exactly:

`POST /v1/agent-platform`

The SDK does not fabricate resource-oriented REST endpoints.

## Installation

```bash
python -m pip install tinlance-agent-platform-sdk
```

## Quick start

```python
from tinlance_agent_platform_sdk import AgentPlatform

client = AgentPlatform(
    base_url="https://platform.example",
    bearer_token="opaque-credential",
    tenant_id="tenant-a",
    subject_id="user-a",
)

health = client.health()
print(health.ready)

agents = client.agents.list()
```

The `tenant_id` and `subject_id` values are request assertions that the Platform verifies against the authenticated principal. They are not local authority grants.

## Authentication and security

The SDK sends an opaque bearer credential:

`Authorization: Bearer <credential>`

It does not assume JWT, OIDC, issuer, audience, or signing semantics. Credential verification is a Platform/deployment responsibility.

Every request has a validated `X-Request-ID`. If one is not supplied, the SDK generates one. Consequential operations send the same request ID as `Idempotency-Key`.

Consequential operations are:

- `runs.create`
- `runs.cancel`
- `approvals.request`

The SDK never automatically retries a consequential operation with a new request ID.

Optional W3C `traceparent` can be supplied to the client and is propagated unchanged after strict validation.

### M0 transport hardening

- HTTPS is required by default; local HTTP requires explicit `allow_insecure_http=True`.
- Automatic redirects are disabled for authenticated requests.
- Response API version must be exactly `1.1`.
- Response media type must be `application/json`.
- Response bodies are bounded (default 8 MiB; configurable with `max_response_bytes`).
- Success envelopes are validated against the specific operation's contract.

See [docs/M0.md](docs/M0.md) for the complete M0 acceptance gates.

## Typed models

The SDK provides immutable typed models for:

- health
- authenticated principal
- agents
- capabilities
- runs
- approval references
- events
- evidence references

Run and approval lifecycle constants are exposed for interpretation. The SDK does not perform client-side lifecycle transitions.

## Errors

Stable Platform HTTP failures map to typed exceptions:

- `InvalidRequestError` — 400
- `AuthenticationError` — 401
- `PermissionError` — 403
- `IdempotencyConflictError` — 409
- `RequestTooLargeError` — 413
- `UnsupportedMediaTypeError` — 415
- `ApiVersionError` — 426
- `PlatformError` — 500 and unknown Platform failures
- `TransportError` — network/transport failure before a valid response

Exceptions preserve the HTTP status and stable Platform error code where available. Authorization tokens are not included in exception messages.

## Deliberately deferred

SDK v0.1 does not expose operations for:

- approval retrieval or approve/reject/cancel
- direct tool execution or registration
- event streaming
- evidence content retrieval
- pagination
- webhooks
- generated OpenAPI clients
- resource-oriented REST paths

Those capabilities must first become versioned Platform API contracts. This prevents the SDK from becoming a second, invented Platform API.

## Architecture boundary

```
tinlance-agent-platform-sdk
        |
        | versioned HTTP contract
        v
Tinlance Agent Platform
        |
        +-- identity / tenant authority
        +-- authorization / policy
        +-- approvals
        +-- governed tools
        +-- secrets / sandbox
        +-- evidence / execution
```

The SDK is not an agent runtime, policy engine, sandbox, secrets manager, tool executor, evidence authority, or replacement for the Agent Platform.

## Repository relationship

The Agent Platform repository contains an internal `packages/sdk` domain/composition package. That package is not this project.

`tinlance-agent-platform-sdk` is the **external network client SDK** and must remain independent of Platform internals.

## Contract

The SDK v0.1 contract is documented in [docs/contracts/SDK-V0.1-CONTRACT.md](docs/contracts/SDK-V0.1-CONTRACT.md).

The server-side forensic baseline remains authoritative in the Tinlance Agent Platform repository. If the server API changes, the server contract and executable tests must change before the SDK expands its public surface.

## Development

```bash
python -m pip install -e ".[test,security]"
python -m pip check
ruff check .
ruff format --check .
mypy src
pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```

Supported Python versions: 3.12, 3.13, and 3.14.

## License

Apache License 2.0. See [LICENSE](LICENSE).


## M1–M11 SDK surface

The repository follows the canonical SDK sequence:

```text
M0 Platform contract discovery
M1 Transport + Client Foundation
M2 Runs + typed models
M3 Approvals + governance
M4 Tools
M5 Evidence + Events
M6 Async API
M7 Research Agent
M8 Security + compatibility hardening
M9 v0.1 release
M10 Production developer experience
M11 v1.0 readiness
```

The complete acceptance contract is [docs/ROADMAP-M0-M11.md](docs/ROADMAP-M0-M11.md).

### Async client

The async client reuses the exact audited synchronous transport rather than maintaining a second HTTP implementation:

```python
from tinlance_agent_platform_sdk import AsyncAgentPlatform, ClientConfig

client = AsyncAgentPlatform(ClientConfig(
    base_url="https://platform.example",
    bearer_token="opaque-credential",
    tenant_id="tenant-a",
    subject_id="user-a",
))
health = await client.health()
```

### Tools

Tool descriptors and invocation/result models are available for SDK composition. They
are metadata contracts only. The SDK cannot authorize or execute a tool locally.

### Research Agent

`ResearchAgent` provides governed research-run composition over the existing
`runs.create` contract. It intentionally does not fabricate model, tool, run-wait,
or run-result endpoints that Platform API 1.1 does not publish.

### Compatibility rule

The public SDK operation set is explicitly declared in
`tinlance_agent_platform_sdk.compat`. New remote operations require a corresponding
versioned Platform contract and executable server conformance tests before they can be
added to the public SDK.
