# Contributing

Thank you for contributing to the Tinlance Agent Platform SDK.

This repository is the **external Agent Developer Surface**. It must remain a thin, typed client contract layer. Do not move Platform authority into the SDK.

## Before you start

1. Read [the documentation index](docs/README.md).
2. Read [SECURITY.md](SECURITY.md) before reporting security-sensitive behavior.
3. Search existing issues and pull requests.
4. For API-surface changes, verify the corresponding versioned Platform contract and executable conformance tests first.

## Development setup

Supported Python versions: 3.12, 3.13, and 3.14.

```bash
python -m pip install -e ".[test,security]"
python -m pip check
ruff check .
ruff format --check .
mypy src
pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```

## Change workflow

1. Fork the repository.
2. Create a focused branch from `main`, for example `feat/<short-name>` or `fix/<short-name>`.
3. Make the smallest change that solves the problem.
4. Add or update tests for behavioral changes.
5. Update documentation and [CHANGELOG.md](CHANGELOG.md) when the public contract changes.
6. Run the full local quality suite.
7. Open a pull request using the repository template.

## SDK boundary rules

The SDK must not become an authority engine. In particular, do not add local implementations of:

- identity or tenant authority;
- authorization or policy decisions;
- approval authority;
- secrets management;
- sandbox enforcement;
- evidence authority;
- Platform execution authority.

New remote operations require a versioned Platform API contract and executable conformance coverage before they become public SDK operations.

## Code standards

- Python 3.12+ with strict typing.
- Keep public models explicit and immutable where the existing API requires it.
- Preserve stable error semantics and request/idempotency behavior.
- Avoid secrets, credentials, customer data, or real tokens in tests and examples.
- Keep dependencies minimal.
- Keep GitHub Actions pinned to immutable commit SHAs.
- Prefer clear, small modules over speculative abstractions.

## Commits

Use Conventional Commit style where practical:

`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `security:`, `chore:`.

Keep commits focused and describe contract changes explicitly.

## Pull requests

A PR should explain:

- what changed and why;
- the affected public API or contract, if any;
- tests run and their results;
- documentation changes;
- security or compatibility impact.

A maintainer may request changes before merge. Passing CI does not replace architectural review.

## License

By contributing, you agree that your contributions are provided under the repository's [Apache License 2.0](LICENSE), unless a separate written agreement states otherwise.
