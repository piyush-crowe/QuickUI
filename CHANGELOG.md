# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] — 2026-05-26
### Added
- `@instantui.chat` decorator — renders a function with a `message` parameter
  (and optional `history`) as a chat card with message log + input box.
  History is held client-side; the server stays stateless.
- New input types: `Literal[...]` and `Enum` → dropdown; `datetime.date` /
  `datetime.datetime` → native pickers; `Annotated[str, instantui.Multiline]`
  → textarea.
- New output types: `instantui.Markdown`, `instantui.HTML`, `instantui.Image`
  wrappers; `pathlib.Path` returns render as download chips (or inline images);
  `list[dict]` and pandas `DataFrame` returns render as HTML tables.
- `instantui.run(title="…")` sets the page heading; CLI gets `--title`.
- Top-of-page nav bar with the "InstantUI" brand mark and a developer line.
- Chat cards now display captured `print()` output above the bot's reply, the
  same way form cards do.
- `docs/` — getting started, forms, chat, types reference, CLI, architecture.

### Changed
- `/run/<idx>` response now returns `result` as a `{kind, value}` block instead
  of a flat string.
- New endpoint `/chat/<idx>` for chat cards; `/run/<idx>` rejects chat indices
  and vice-versa.
- `cast_value(value, field)` now takes the full `Field` (was `type_name`).


## [0.1.0] — 2026-05-26
### Added
- `@instantui.app` decorator to register functions as UI cards.
- `instantui.run(host, port, open_browser, registry)` to serve the UI.
- `instantui` CLI: `instantui script.py [--host --port --no-browser]`.
- Type-driven input rendering for `str`, `int`, `float`, `bool`.
- Captured stdout shown alongside the return value.
- Zero runtime dependencies.
