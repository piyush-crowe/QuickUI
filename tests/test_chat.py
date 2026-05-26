"""Tests for the chat decorator, /chat/<idx> endpoint, and chat card rendering."""

from __future__ import annotations

import json
import threading
import urllib.request
from http.server import HTTPServer

import pytest

from instantui.core.registry import Registry
from instantui.rendering import render_index
from instantui.server.handler import make_handler

# ----- registry ---------------------------------------------------------------


def test_register_chat_requires_message_param():
    reg = Registry()
    with pytest.raises(ValueError):

        @reg.register_chat
        def bad():
            return "no message"


def test_register_chat_creates_entry_with_kind():
    reg = Registry()

    @reg.register_chat
    def bot(message: str) -> str:
        return message

    assert len(reg) == 1
    assert reg[0].kind == "chat"
    assert reg[0].fields == []


# ----- rendering --------------------------------------------------------------


def test_render_index_emits_chat_markup():
    reg = Registry()

    @reg.register_chat
    def bot(message: str) -> str:
        return message

    html = render_index(reg.entries)
    assert 'class="chat"' in html
    assert 'class="chat__log"' in html
    assert 'class="chat__input"' in html


def test_form_and_chat_coexist():
    reg = Registry()

    @reg.register
    def add(a: int, b: int) -> int:
        return a + b

    @reg.register_chat
    def bot(message: str) -> str:
        return message

    html = render_index(reg.entries)
    # form card present
    assert 'class="card__form"' in html
    # chat card present
    assert 'class="card card--chat"' in html


# ----- live endpoint ----------------------------------------------------------


@pytest.fixture
def chat_server():
    reg = Registry()

    @reg.register_chat
    def echo(message: str, history: list) -> str:
        return f"you said: {message} (turn {len(history) + 1})"

    @reg.register_chat
    def no_history(message: str) -> str:
        # function without history param — handler should not pass it
        return message.upper()

    @reg.register
    def add(a: int, b: int) -> int:
        return a + b

    handler = make_handler(reg)
    server = HTTPServer(("127.0.0.1", 0), handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}", reg
    finally:
        server.shutdown()
        server.server_close()
        t.join(timeout=1)


def _post(url: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def test_chat_endpoint_passes_message_and_history(chat_server):
    url, _ = chat_server
    out = _post(
        url + "/chat/0",
        {
            "message": "hi",
            "history": [{"role": "user", "content": "earlier"}],
        },
    )
    assert out["ok"] is True
    assert out["reply"]["kind"] == "markdown"
    assert "you said: hi (turn 2)" in out["reply"]["value"]


def test_chat_endpoint_skips_history_when_unwanted(chat_server):
    url, _ = chat_server
    out = _post(url + "/chat/1", {"message": "hello"})
    assert out["ok"] is True
    assert out["reply"]["value"] == "HELLO"


def test_chat_endpoint_captures_stdout():
    reg = Registry()

    @reg.register_chat
    def loud(message: str) -> str:
        print("step 1")
        print("step 2")
        return message

    handler = make_handler(reg)
    server = HTTPServer(("127.0.0.1", 0), handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        host, port = server.server_address
        out = _post(f"http://{host}:{port}/chat/0", {"message": "hi"})
    finally:
        server.shutdown()
        server.server_close()
        t.join(timeout=1)

    assert out["ok"] is True
    assert "step 1" in out["stdout"]
    assert "step 2" in out["stdout"]


def test_chat_endpoint_rejects_form_index(chat_server):
    url, _ = chat_server
    # index 2 is the form-style `add`; /chat/2 must 404.
    req = urllib.request.Request(
        url + "/chat/2",
        data=b'{"message":"x"}',
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(req)
    assert exc.value.code == 404


def test_run_endpoint_rejects_chat_index(chat_server):
    url, _ = chat_server
    req = urllib.request.Request(
        url + "/run/0",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(req)
    assert exc.value.code == 404
