# Security Policy

## Scope

This repository contains the external Python SDK for the Tinlance Agent Platform. The SDK is a client contract layer. Authentication, authorization, tenant authority, policy, approvals, tool permissions, secrets, sandboxing, execution, and evidence authority remain server-side Platform responsibilities.

## Reporting a vulnerability

**Do not disclose suspected vulnerabilities in public issues or pull requests.**

Use GitHub's private vulnerability reporting for this repository:

https://github.com/LloydCoder/tinlance-agent-platform-sdk/security/advisories/new

If private reporting is unavailable, email **hello@tinlance.com** with the subject Security vulnerability — Tinlance Agent Platform SDK.

Include:

- affected version and commit;
- reproducible steps or a minimal proof of concept;
- expected and observed behavior;
- security impact and plausible attack path;
- relevant logs with credentials and personal data removed.

Do not include live credentials, access tokens, private keys, customer data, or unnecessary personal information.

## Response targets

- **Acknowledgement:** within 3 business days.
- **Initial triage:** within 7 business days.
- **Remediation:** prioritized according to severity, exploitability, affected surface, and release risk.

These are response targets, not a guarantee of a fixed remediation date.

## Security boundary

The SDK is designed to:

- require HTTPS by default;
- disable redirects for authenticated Platform requests;
- validate Platform API version and JSON media type;
- bound response bodies;
- propagate request IDs and consequential idempotency keys;
- fail closed on malformed success and error envelopes;
- avoid automatic retries of consequential operations unless explicitly configured;
- avoid placing authorization tokens in exception messages;
- keep authorization and execution authority in the Platform.

## Supply-chain controls

CI currently:

- pins GitHub Actions to immutable commit SHAs;
- uses least-privilege workflow permissions;
- runs dependency auditing with pip-audit;
- generates a CycloneDX SBOM;
- runs CodeQL;
- uses Dependabot for GitHub Actions and Python dependency updates;
- builds and smoke-tests release artifacts;
- uses PyPI Trusted Publishing/OIDC rather than a long-lived PyPI token;
- generates build provenance attestations.

## Disclosure

We will coordinate disclosure with reporters where practical. Security fixes should include regression coverage and a changelog entry when the affected behavior is user-visible.
