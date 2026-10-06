# Documentation

This directory is the durable technical documentation for the Tinlance Agent Platform SDK.

Historical milestone documents remain intact while this index provides a Diátaxis-oriented navigation model.

## Tutorials

Goal: learn by following a complete path.

- [README quick start](../README.md#quick-start)
- [Async example](../examples/basic_async.py)

## How-to guides

Goal: solve a specific development task.

- [Contributing](../CONTRIBUTING.md)
- [Security reporting](../SECURITY.md)
- [M0 transport hardening](M0.md)
- [M12–M20 program](M12-M20.md)

## Explanation

Goal: understand architecture and design decisions.

- [M21 program](M21.md)
- [SDK v1.0 contract](contracts/SDK-V1.0-CONTRACT.md)
- [Compatibility matrix](contracts/compatibility-matrix.json)
- [Security control matrix](security/m21-6-control-matrix.json)
- [Historical M0–M11 roadmap](ROADMAP-M0-M11.md)

## Reference

Goal: look up exact contracts and machine-readable definitions.

- [SDK contract manifest](contracts/sdk-contract-manifest.json)
- [M21.1 Platform conformance](M21.1.md)
- [M21.2 Agent developer surface](M21.2.md)
- [M21.3 Run lifecycle readiness](M21.3.md)
- [M21.4 MCP tooling surface](M21.4.md)
- [M21.5 Observability and evaluation](M21.5.md)
- [M21.6 Security and supply-chain certification](M21.6.md)
- [M21.7 Enterprise release and certification](M21.7.md)

## Documentation rules

- Prefer relative links for repository-local content.
- Keep Platform authority in the Platform repository; do not copy authoritative server semantics into the SDK.
- Update contract documents and tests together when the public API changes.
- Keep examples runnable and free of real credentials.
- Use root llms.txt as the concise agent-facing entry point.
