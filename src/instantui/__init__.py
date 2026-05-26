"""InstantUI — wrap a Python function and get an instant web UI."""

from instantui._version import __version__
from instantui.core.registry import app, chat, registry
from instantui.exceptions import InstantUIError, NoFunctionsRegisteredError
from instantui.server.runner import run
from instantui.types import HTML, Image, Markdown, Multiline

__all__ = [
    "__version__",
    "app",
    "chat",
    "run",
    "registry",
    "HTML",
    "Image",
    "Markdown",
    "Multiline",
    "InstantUIError",
    "NoFunctionsRegisteredError",
]
