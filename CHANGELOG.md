# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-05-26
### Added
- `@instantui.app` decorator to register functions as UI cards.
- `instantui.run(host, port, open_browser, registry)` to serve the UI.
- `instantui` CLI: `instantui script.py [--host --port --no-browser]`.
- Type-driven input rendering for `str`, `int`, `float`, `bool`.
- Captured stdout shown alongside the return value.
- Zero runtime dependencies.
