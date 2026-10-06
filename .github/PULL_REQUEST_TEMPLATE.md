## Summary

<!-- What changed and why? -->

## Contract and architecture

- [ ] I verified that this change preserves the SDK → Platform authority boundary.
- [ ] New remote operations have a versioned Platform contract and executable conformance coverage.
- [ ] No Platform implementation package is imported.

## Validation

- [ ] `python -m pip check`
- [ ] `ruff check .`
- [ ] `ruff format --check .`
- [ ] `mypy src`
- [ ] `pytest --cov=src --cov-fail-under=90`
- [ ] Relevant security/supply-chain checks pass.

## Documentation

- [ ] README/docs updated when behavior or public API changed.
- [ ] CHANGELOG.md updated for user-visible changes.

## Security and compatibility

- [ ] No credentials, private keys, customer data, or secrets are included.
- [ ] Backward compatibility was considered.
- [ ] Error, idempotency, tracing, and retry semantics were preserved or intentionally documented.

## Reviewer notes

<!-- Include migration notes, release considerations, or known limitations. -->
