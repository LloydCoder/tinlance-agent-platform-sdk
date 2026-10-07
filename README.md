# Tinlance Agent Platform SDK

<div align="center">

**A typed Python developer surface for building agents against the Tinlance Agent Platform's governed execution boundary.**

[![CI](https://github.com/LloydCoder/tinlance-agent-platform-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/LloydCoder/tinlance-agent-platform-sdk/actions/workflows/ci.yml)
[![Security](https://github.com/LloydCoder/tinlance-agent-platform-sdk/actions/workflows/security.yml/badge.svg)](https://github.com/LloydCoder/tinlance-agent-platform-sdk/actions/workflows/security.yml)
[![License](https://img.shields.io/github/license/LloydCoder/tinlance-agent-platform-sdk)](LICENSE)

</div>

> [!NOTE]
> The SDK is a client contract layer. The Tinlance Agent Platform remains authoritative for identity, tenant binding, authorization, policy, approvals, secrets, sandboxing, execution, and evidence.

## Visual proof

The executable architecture is intentionally simple:

~~~mermaid
flowchart LR
    D[Tinlance Agent Developer] --> O[Tinlance Agent OS]
    A[Agent application] --> B[Tinlance Agent Platform SDK]
    O --> B
    B -->|versioned HTTP 1.1 contract| C[Tinlance Agent Platform]
    C --> D[Identity / tenant authority]
    C --> E[Policy / approvals]
    C --> F[Governed execution / tools]
    C --> G[Evidence / audit]
    X[Ecosystem Conformance] -. verifies .-> D
    X -. verifies .-> O
    X -. verifies .-> B
    X -. verifies .-> C
~~~

The SDK exposes typed contracts and safe client-side composition without creating a second runtime or authority plane.

The ecosystem conformance gate maintained by TADL verifies this SDK against the same Platform reference boundary used by Agent OS. See [Ecosystem conformance](docs/integration/CONFORMANCE.md).

## Why this SDK

| Concern | SDK | Platform |
| --- | --- | --- |
| Typed developer API | Yes | Contract source |
| Agent metadata and lifecycle interpretation | Yes | Authoritative state |
| Request IDs and idempotency helpers | Yes | Enforcement |
| Trace-context propagation | Yes | Observability authority |
| Authorization and policy | No | **Authoritative** |
| Approvals | Request/composition surface | **Authoritative** |
| Secrets and sandboxing | No | **Authoritative** |
| Tool execution | Contract surface only | **Authoritative** |
| Evidence validity | Opaque references | **Authoritative** |

This separation keeps the public SDK independently installable while preventing client-side policy drift.

## Quick Start

### 1. Clone and install

~~~bash
git clone https://github.com/LloydCoder/tinlance-agent-platform-sdk.git
cd tinlance-agent-platform-sdk
python -m pip install -e .
~~~

### 2. Verify the installed package

~~~bash
tinlance-agent-sdk
~~~

### 3. Run a typed client call against your Platform deployment

~~~python
from tinlance_agent_platform_sdk import AgentPlatform

client = AgentPlatform(
    base_url="https://platform.example",
    bearer_token="opaque-credential",
    tenant_id="tenant-a",
    subject_id="user-a",
)

health = client.health()
print(health.ready)
~~~

> [!WARNING]
> Replace the example URL and credential with values from your Platform deployment. The SDK does not validate or mint credentials locally.

## Installation

**Prerequisites**

- Python 3.12, 3.13, or 3.14.
- Network access to a compatible Tinlance Agent Platform API 1.1 deployment when making remote calls.

**From source**

~~~bash
git clone https://github.com/LloydCoder/tinlance-agent-platform-sdk.git
cd tinlance-agent-platform-sdk
python -m pip install .
~~~

**Editable development install**

~~~bash
python -m pip install -e ".[test,security]"
~~~

The package has no mandatory runtime dependencies. A GitHub release is not currently published; use the source installation above until the first PyPI release is announced.

## Usage

### Synchronous client

~~~python
from tinlance_agent_platform_sdk import AgentPlatform

client = AgentPlatform(
    base_url="https://platform.example",
    bearer_token="opaque-credential",
    tenant_id="tenant-a",
    subject_id="user-a",
)

print(client.health().ready)
agents = client.agents.list()
~~~

### Asynchronous client

~~~python
from tinlance_agent_platform_sdk import AsyncAgentPlatform, ClientConfig

client = AsyncAgentPlatform(
    ClientConfig(
        base_url="https://platform.example",
        bearer_token="opaque-credential",
        tenant_id="tenant-a",
        subject_id="user-a",
    )
)

health = await client.health()
print(health.ready)
~~~

See [examples/basic_async.py](examples/basic_async.py) for the repository's runnable async example.

### Public operation surface

| SDK method | Platform operation |
| --- | --- |
| health() | health |
| principal.get() | principal.get |
| agents.list() | agents.list |
| capabilities.list(agent_id) | capabilities.list |
| runs.create(...) | runs.create |
| runs.cancel(run_id) | runs.cancel |
| approvals.request(...) | approvals.request |
| approvals.decide(...) | approvals.decide |
| tools.execute(...) | tools.execute |
| executions.get(execution_id) | executions.get |
| runs.events(run_id) | runs.events |
| runs.evidence(run_id) | runs.evidence |

The wire boundary is POST /v1/agent-platform. The SDK does not invent resource-oriented REST paths.

## Configuration / Options

| Option | Default | Purpose |
| --- | --- | --- |
| base_url | Required | Platform API origin |
| bearer_token | Optional when a credential provider is used | Opaque bearer credential |
| tenant_id | Optional | Request assertion verified by Platform |
| subject_id | Optional | Request assertion verified by Platform |
| allow_insecure_http | False | Explicit opt-in for local HTTP |
| max_response_bytes | 8 MiB | Response-size bound |
| RetryPolicy | Conservative | Bounded transient retry behavior |
| TraceContext | None | W3C trace-context propagation |
| credential_provider | None | Caller-owned short-lived credential rotation |
| Custom CA / mTLS / proxy | None | Enterprise transport configuration |

Consequential operations are not automatically retried unless the caller explicitly enables that policy.

## Features

| Capability | Status |
| --- | --- |
| Typed R10 developer contracts | Stable |
| Sync and async clients | Stable |
| Lifecycle interpretation helpers | Stable |
| Capability metadata | Stable |
| Approval workflow composition | Stable |
| Governed execution/result models | Stable |
| Opaque evidence references | Stable |
| Structured errors | Stable |
| Explicit idempotency helpers | Stable |
| W3C trace-context propagation | Stable |
| MCP integration metadata | Stable |
| Payload-free telemetry hooks | Stable |
| Enterprise credential rotation | Stable |
| SBOM and provenance release controls | Stable |
| Local diagnostics | Stable |

Contract-gated surfaces such as streaming, pagination, webhooks, evidence-content retrieval, and generated protocol clients are added only after the Platform publishes a versioned contract and executable conformance tests.

## Security Model

The SDK requires HTTPS by default, disables redirects for authenticated requests, validates API version and response media type, bounds response bodies, and avoids leaking authorization tokens through exceptions.

The SDK does **not** decide whether a caller is authorized. It transports assertions and credentials to the Platform, where identity, tenant isolation, policy, approval authority, secrets, sandboxing, execution, and evidence validity are enforced.

Read [SECURITY.md](SECURITY.md) before handling security-sensitive issues.

## Documentation

- [P10 — Replication & Agent System GA](docs/ecosystem/P10-REPLICATION-GA.md)

- [Documentation index](docs/README.md)
- [SDK v1.0 contract](docs/contracts/SDK-V1.0-CONTRACT.md)
- [Contract manifest](docs/contracts/sdk-contract-manifest.json)
- [Compatibility matrix](docs/contracts/compatibility-matrix.json)
- [M21 program](docs/M21.md)
- [M12–M20 program](docs/M12-M20.md)
- [M0 transport hardening](docs/M0.md)
- [Async example](examples/basic_async.py)

For agent-facing discovery, see [llms.txt](llms.txt).

## Development

~~~bash
python -m pip install -e ".[test,security]"
python -m pip check
ruff check .
ruff format --check .
mypy src
pytest --cov=src --cov-report=term-missing --cov-fail-under=90
~~~

CI runs the supported Python matrix, type/lint/format checks, coverage enforcement, dependency auditing, SBOM generation, package smoke tests, and CodeQL.

## Contributing

Contributions are welcome when they preserve the SDK/Platform boundary.

Start with [CONTRIBUTING.md](CONTRIBUTING.md), then open a focused pull request using the repository template.

## License + Acknowledgements

Copyright 2026 Tinlance Limited.

Licensed under the [Apache License 2.0](LICENSE). See [NOTICE](NOTICE) for attribution information.

The SDK uses standard Python packaging, typing, testing, and GitHub Actions tooling. See [pyproject.toml](pyproject.toml) for the supported development toolchain.

<details>
<summary>Roadmap and contract gates</summary>

The historical delivery sequence is preserved in [docs/ROADMAP-M0-M11.md](docs/ROADMAP-M0-M11.md) and the M12–M21 program documents.

New public operations remain contract-gated: the server-side Platform contract and executable conformance tests are authoritative before SDK expansion.

</details>

<details>
<summary>Troubleshooting</summary>

**Import fails after installation**

~~~bash
python -c "import sys, tinlance_agent_platform_sdk as sdk; print(sys.executable); print(sdk.SDK_VERSION)"
python -m pip check
~~~

**Platform request fails**

Check the Platform URL, credential, tenant/subject assertions, API version, and network connectivity. Do not paste credentials into issues.

**A feature is missing**

Check the contract documentation first. A capability may be intentionally deferred until the Platform publishes a versioned contract.

</details>

<details>
<summary>Support</summary>

See [SUPPORT.md](SUPPORT.md). Security issues must follow [SECURITY.md](SECURITY.md) rather than a public issue.

</details>
