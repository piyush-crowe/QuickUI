"""Bootstrap and run the InstantUI HTTP server."""

from __future__ import annotations

import logging
import webbrowser
from http.server import HTTPServer

from instantui.core.registry import Registry
from instantui.core.registry import registry as default_registry
from instantui.exceptions import NoFunctionsRegisteredError
from instantui.server.handler import make_handler

logger = logging.getLogger("instantui")


def run(
    host: str = "127.0.0.1",
    port: int = 8000,
    *,
    title: str | None = None,
    open_browser: bool = True,
    registry: Registry | None = None,
) -> None:
    """Start the InstantUI server on ``host:port`` and block.

    ``title`` is shown as the page heading (e.g. your app's name). The small
    "InstantUI" brand mark stays in the top-left regardless.

    Raises :class:`NoFunctionsRegisteredError` if nothing has been registered.
    """
    reg = registry or default_registry
    if not len(reg):
        raise NoFunctionsRegisteredError(
            "No functions registered. Decorate one with @instantui.app first."
        )

    handler_cls = make_handler(reg, title=title)
    server = HTTPServer((host, port), handler_cls)
    url = f"http://{host}:{port}"
    print(f"InstantUI running on {url}  (Ctrl+C to stop)")

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001
            logger.debug("could not open browser", exc_info=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down…")
    finally:
        server.server_close()
