# Contributing

Thanks for considering a contribution to InstantUI.

## Quick start

```bash
git clone https://github.com/piyushpy/QuickUI.git
cd QuickUI
python -m venv .venv && source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

## Workflow

1. Open an issue describing the change — especially for new public API.
2. Branch from `development`. Keep commits focused.
3. Add tests for any behavior change. The suite must pass:
   ```bash
   pytest
   ruff check .
   mypy
   ```
4. Update `CHANGELOG.md` under `[Unreleased]`.
5. Open a PR against `development`.

## Code style

- `ruff` is the source of truth for formatting and lint.
- Public functions get a one-line docstring; explain *why* in comments only when non-obvious.
- Keep the runtime dependency list empty. Dev-only deps go under `[project.optional-dependencies] dev`.

## Layout

The package lives under `src/instantui/`. Each subpackage has a single responsibility — keep them independently importable and testable.

## Reporting bugs

Open an issue with the smallest reproduction you can produce (the decorated function plus how you launched the server). Include Python version and OS.
