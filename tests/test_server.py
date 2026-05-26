"""End-to-end tests that boot an HTTPServer on an ephemeral port."""

from __future__ import annotations

import json
import threading
import urllib.request
from http.server import HTTPServer

import pytest

from instantui.core.registry import Registry
from instantui.server.handler import make_handler


@pytest.fixture
def live_server():
    reg = Registry()

    @reg.register
    def echo(msg: str = "hi") -> str:
        print("side effect")
        return msg.upper()

    @reg.register
    def boom() -> str:
        raise RuntimeError("nope")

    handler = make_handler(reg)
    server = HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)


def _get(url: str) -> tuple[int, bytes, str]:
    with urllib.request.urlopen(url) as resp:
        return resp.status, resp.read(), resp.headers.get_content_type()


def _post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def test_index_renders(live_server: str):
    status, body, ctype = _get(live_server + "/")
    assert status == 200
    assert ctype == "text/html"
    assert b"echo" in body


def test_static_css(live_server: str):
    status, body, ctype = _get(live_server + "/static/style.css")
    assert status == 200
    assert ctype == "text/css"
    assert b":root" in body


def test_run_success(live_server: str):
    result = _post_json(live_server + "/run/0", {"msg": "hey"})
    assert result["ok"] is True
    assert result["result"] == {"kind": "text", "value": "HEY"}
    assert "side effect" in result["stdout"]


def test_run_error_returns_traceback(live_server: str):
    result = _post_json(live_server + "/run/1", {})
    assert result["ok"] is False
    assert "RuntimeError" in result["error"]
