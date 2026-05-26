"""HTTP handler that serves the InstantUI index and dispatches function calls."""

from __future__ import annotations

import contextlib
import inspect
import io
import json
import logging
import traceback
from http.server import BaseHTTPRequestHandler
from typing import Any

from instantui.core.casting import cast_value
from instantui.core.registry import Registry
from instantui.output import render_result
from instantui.rendering import render_index, static_asset
from instantui.types import HTML, Image, Markdown

logger = logging.getLogger("instantui.server")


def _chat_block(result: Any) -> dict[str, Any]:
    """Render a chat reply. Plain strings default to Markdown."""
    if isinstance(result, str) and not isinstance(result, (Markdown, HTML)) \
            and not isinstance(result, Image):
        return render_result(Markdown(result))
    return render_result(result)


def make_handler(
    registry: Registry,
    *,
    title: str | None = None,
) -> type[BaseHTTPRequestHandler]:
    """Build a :class:`BaseHTTPRequestHandler` subclass bound to ``registry``.

    ``title`` is shown as the page heading; if ``None`` only the brand mark
    appears.
    """

    class _Handler(BaseHTTPRequestHandler):
        server_version = "InstantUI"

        def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A003
            logger.debug("%s - %s", self.address_string(), fmt % args)

        # ---- response helpers ------------------------------------------------
        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, status: int, payload: dict[str, Any]) -> None:
            self._send(status, json.dumps(payload).encode("utf-8"), "application/json")

        def _not_found(self) -> None:
            self._send(404, b"not found", "text/plain; charset=utf-8")

        # ---- routes ----------------------------------------------------------
        def do_GET(self) -> None:  # noqa: N802
            if self.path in ("/", "/index.html"):
                body = render_index(registry.entries, title=title).encode("utf-8")
                self._send(200, body, "text/html; charset=utf-8")
                return
            if self.path.startswith("/static/"):
                asset = static_asset(self.path[len("/static/"):])
                if asset is None:
                    self._not_found()
                    return
                body, mime = asset
                self._send(200, body, mime)
                return
            self._not_found()

        def do_POST(self) -> None:  # noqa: N802
            if self.path.startswith("/run/"):
                self._dispatch_run()
                return
            if self.path.startswith("/chat/"):
                self._dispatch_chat()
                return
            self._not_found()

        # ---- dispatchers -----------------------------------------------------
        def _entry_at(self, prefix: str):
            try:
                idx = int(self.path.removeprefix(prefix))
                return idx, registry[idx]
            except (ValueError, IndexError):
                return None, None

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            return json.loads(raw or "{}")

        def _dispatch_run(self) -> None:
            _, entry = self._entry_at("/run/")
            if entry is None or entry.kind != "form":
                self._not_found()
                return
            try:
                payload = self._read_json()
                kwargs = {
                    f.name: cast_value(payload[f.name], f)
                    for f in entry.fields
                    if f.name in payload
                }
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    result = entry.fn(**kwargs)
                self._send_json(
                    200,
                    {"ok": True, "result": render_result(result), "stdout": buf.getvalue()},
                )
            except Exception as exc:  # noqa: BLE001
                self._send_json(
                    200,
                    {
                        "ok": False,
                        "error": f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
                    },
                )

        def _dispatch_chat(self) -> None:
            _, entry = self._entry_at("/chat/")
            if entry is None or entry.kind != "chat":
                self._not_found()
                return
            try:
                payload = self._read_json()
                message = str(payload.get("message", ""))
                history = payload.get("history", [])
                if not isinstance(history, list):
                    history = []

                sig_params = inspect.signature(entry.fn).parameters
                kwargs: dict[str, Any] = {"message": message}
                if "history" in sig_params:
                    kwargs["history"] = history

                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    result = entry.fn(**kwargs)
                self._send_json(
                    200,
                    {
                        "ok": True,
                        "reply": _chat_block(result),
                        "stdout": buf.getvalue(),
                    },
                )
            except Exception as exc:  # noqa: BLE001
                self._send_json(
                    200,
                    {
                        "ok": False,
                        "error": f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
                    },
                )

    return _Handler
