# P1 Transformation Contract

The SDK exposes the authority-neutral `Transformation` model as a typed developer contract.

It records business intent and execution/outcome references but cannot grant capability, authorize a principal, approve an action, or execute a tool. The Platform must independently enforce authorization and policy.

The canonical wire shape is `transformation/v1`. The model provides deterministic SHA-256 content digests for correlation and integrity checks; consumers must not treat the digest as authorization evidence.
