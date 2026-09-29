# Security Policy

## Scope

This repository contains the external Python SDK for the Tinlance Agent Platform. The SDK is a client contract layer; authentication, authorization, policy, approvals, tool permission, secrets, sandboxing, execution, and evidence authority remain server-side Platform responsibilities.

## Reporting a vulnerability

Please do not disclose suspected vulnerabilities in public issues. Report them privately to the repository maintainers through the security contact configured for this project.

Include:
- affected version and commit;
- reproducible steps or proof of concept;
- expected and observed behavior;
- security impact;
- relevant logs with credentials and personal data removed.

Do not include live credentials, access tokens, private keys, or customer data.

## Security guarantees

The SDK is designed to:
- require HTTPS by default;
- disable HTTP redirects for authenticated Platform requests;
- validate Platform API version and JSON media type on responses;
- bound response bodies;
- propagate caller request IDs and consequential idempotency keys;
- fail closed on malformed success and error envelopes;
- avoid automatic retries of consequential operations;
- keep authorization and execution authority in the Platform.

## Supply-chain controls

CI pins GitHub Actions to immutable commit SHAs, uses least-privilege workflow permissions, audits Python dependencies, generates an SBOM, and runs CodeQL, pip-audit, and Dependabot dependency updates. Release publishing uses PyPI Trusted Publishing/OIDC rather than a long-lived PyPI token.
