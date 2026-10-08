# TSIC Integration

The SDK is the developer/client surface for Agent Platform. It is not an authorization or execution authority.

TSIC is the canonical ecosystem integration and certification authority. Agent Platform remains authoritative for identity, authorization, policy, runtime, approvals, tools/MCP, secrets, budgets, evidence, audit, and observability.

The SDK CI gate consumes the immutable TSIC revision 28336e26b648f438ae03ebaf03a48b7b421cde31 and validates:

- repository identity and governance role;
- contract binding set;
- Platform execution authority;
- SDK non-authority invariants;
- identity, idempotency, trace and interoperability metadata requirements.

Run locally with:

    python scripts/tsic_conformance.py

Passing this check certifies compatibility with the pinned TSIC contract surface. It does not grant the SDK authority and does not claim that a Platform deployment is production-ready.
