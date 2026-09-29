# Tinlance Agent Platform SDK — M0–M11 Completion Contract

This document reconciles the SDK roadmap with the executable Platform v1.1 contract.

| Phase | Outcome | Boundary |
|---|---|---|
| M0 | Platform contract discovery + transport hardening | exact v1.1 operation gateway |
| M1 | Transport + client foundation | immutable config, secure transport, user-agent, shared sync core |
| M2 | Runs + typed models | immutable run/approval/event/evidence models and lifecycle validation |
| M3 | Approvals + governance | approval request contract; no client-side authority |
| M4 | Tools | typed tool descriptors/invocations; execution remains Platform-owned |
| M5 | Evidence + Events | typed event/evidence reference surfaces |
| M6 | Async API | async facade over the audited sync transport |
| M7 | Research Agent | governed research-run composition; no invented polling/model API |
| M8 | Security + compatibility hardening | HTTPS, redirect, response bounds/version/media checks, explicit compatibility matrix |
| M9 | v0.1 release | release-ready packaging, build verification, trusted-publishing workflow |
| M10 | Production developer experience | docs, examples, stable imports, type metadata, changelog |
| M11 | v1.0 readiness | API freeze/compatibility contract and regression gates |

## Authority rule

The SDK never becomes an authority engine. Authentication, tenant authority,
authorization, policy, approval decisions, tool permission, secrets, sandboxing,
execution and evidence validity remain Platform responsibilities.

M4 and M7 deliberately do not invent HTTP operations absent from Platform v1.1.
Current MCP guidance similarly treats authorization and protected-tool enforcement
as server-side boundaries, while the 2026 MCP release emphasizes explicit,
versioned extensions for capabilities such as tasks and authorization. This keeps
the SDK interoperable instead of creating a private incompatible protocol.

## Release gate

A phase is complete only when its implementation, tests, documentation, typing,
security checks and CI are green and merged.
