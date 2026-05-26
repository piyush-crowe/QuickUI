"""HTTP server that exposes the InstantUI registry over a local web UI."""

from instantui.server.handler import make_handler
from instantui.server.runner import run

__all__ = ["make_handler", "run"]
