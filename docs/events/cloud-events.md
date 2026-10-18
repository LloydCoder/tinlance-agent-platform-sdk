# CloudEvents 1.0 SDK Contract

`CloudEvent` serializes the approved event contract using CloudEvents attribute names (`specversion`, `id`, `source`, `type`, `time`, `datacontenttype`) and lower-case alphanumeric extension names. Tenant, execution, trace and correlation metadata are context for routing and observability, not authorization claims.

The payload is recursively immutable after construction. `as_payload()` returns a fresh JSON-compatible object for serialization. Invalid timestamps, zero/invalid W3C trace identifiers, malformed HTTP(S) URI references, embedded URI credentials, non-finite JSON values, unsupported data classifications and unsupported spec versions fail closed.

The SDK does not decide whether a consumer is authorized to act on an event. Consumers must validate against the exact TSIC schema and derive tenant identity from authenticated Platform context. Delivery is at-least-once; consumers must deduplicate on `source + id` and commit inbox receipts with business effects before acknowledgement.
