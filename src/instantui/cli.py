"""Command-line entry point: ``instantui path/to/script.py``."""

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path

from instantui import __version__
from instantui.server.runner import run


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="instantui",
        description="Run an InstantUI server for a Python script that registers functions.",
    )
    parser.add_argument(
        "script",
        nargs="?",
        type=Path,
        help="Path to a Python file that decorates functions with @instantui.app.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1).")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000).")
    parser.add_argument(
        "--title",
        default=None,
        help="Heading shown above the cards (defaults to no heading).",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the browser automatically.",
    )
    parser.add_argument("--version", action="version", version=f"instantui {__version__}")
    return parser


def _load_script(path: Path) -> None:
    if not path.exists():
        sys.exit(f"instantui: script not found: {path}")
    # runpy executes the file in its own namespace; decorators register on import.
    runpy.run_path(str(path), run_name="__main__")


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.script is None:
        parser.print_help()
        sys.exit(2)

    _load_script(args.script)
    run(
        host=args.host,
        port=args.port,
        title=args.title,
        open_browser=not args.no_browser,
    )


if __name__ == "__main__":
    main()
