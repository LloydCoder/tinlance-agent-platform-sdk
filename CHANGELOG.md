# Changelog

All notable changes to the Tinlance Agent Platform SDK are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow Semantic Versioning.

## [Unreleased]

### Changed

- Documentation and community-health files are being aligned with the 2026 repository standard.

## [1.0.0] - 2026-10-03

### Added

- Enterprise GA external SDK for Tinlance Agent Platform API 1.1.
- Governed R10 developer-surface contracts and agent scaffolding.
- Bounded transient retry support with `Retry-After` handling.
- Optional payload-free telemetry hooks.
- Enterprise credential-provider, custom CA, mTLS, and proxy configuration.
- Compatibility and security certification matrices.
- SBOM and build-provenance release controls.
- Safe local diagnostics through `tinlance-agent-sdk`.
- M21.1–M21.7 conformance, developer-surface, lifecycle, MCP, observability/evaluation, security, and release gates.

### Changed

- Reconciled public documentation with the Platform authority boundary.
- Kept the SDK independent from Platform implementation packages.

## [0.1.0] - 2026-09-29

### Added

- Initial external SDK for Tinlance Agent Platform API 1.1.

[Unreleased]: https://github.com/LloydCoder/tinlance-agent-platform-sdk/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/LloydCoder/tinlance-agent-platform-sdk/releases/tag/v1.0.0
[0.1.0]: https://github.com/LloydCoder/tinlance-agent-platform-sdk/releases/tag/v0.1.0
