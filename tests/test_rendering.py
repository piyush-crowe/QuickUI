from datetime import date
from typing import Annotated, Literal

from instantui.core.registry import Registry
from instantui.rendering import render_index, static_asset
from instantui.types import Multiline


def test_render_index_contains_function_name():
    reg = Registry()

    @reg.register
    def add(a: int, b: int = 2) -> int:
        """Add two numbers."""
        return a + b

    html = render_index(reg.entries)
    assert "add" in html
    assert "Add two numbers." in html
    assert 'name="a"' in html
    assert 'name="b"' in html
    assert 'value="2"' in html


def test_render_index_escapes_doc():
    reg = Registry()

    @reg.register
    def f():
        """<script>x</script>"""
        return None

    html = render_index(reg.entries)
    assert "<script>x</script>" not in html
    assert "&lt;script&gt;" in html


def test_static_asset_serves_css_and_js():
    css = static_asset("style.css")
    js = static_asset("app.js")
    assert css is not None and css[1].startswith("text/css")
    assert js is not None and js[1].startswith("application/javascript")


def test_static_asset_unknown_returns_none():
    assert static_asset("missing.png") is None
    assert static_asset("nope.css") is None


def test_render_select_for_literal():
    reg = Registry()

    @reg.register
    def f(mode: Literal["fast", "slow"] = "slow"):
        return mode

    html = render_index(reg.entries)
    assert "<select" in html
    assert 'value="fast"' in html
    assert 'value="slow" selected' in html


def test_render_textarea_for_multiline():
    reg = Registry()

    @reg.register
    def f(body: Annotated[str, Multiline] = "x"):
        return body

    html = render_index(reg.entries)
    assert "<textarea" in html
    assert "x</textarea>" in html


def test_render_index_with_title():
    reg = Registry()

    @reg.register
    def f():
        return None

    html = render_index(reg.entries, title="My App")
    assert '<h1 class="page__title">My App</h1>' in html
    assert 'class="nav"' in html
    assert ">InstantUI</span>" in html
    assert "developer: piyush" in html


def test_render_index_without_title_hides_h1():
    reg = Registry()

    @reg.register
    def f():
        return None

    html = render_index(reg.entries)
    assert 'class="page__title"' not in html
    assert 'class="nav"' in html
    assert ">InstantUI</span>" in html
    assert "developer: piyush" in html


def test_render_index_escapes_title():
    reg = Registry()

    @reg.register
    def f():
        return None

    html = render_index(reg.entries, title="<x>")
    assert "<x>" not in html
    assert "&lt;x&gt;" in html


def test_render_date_input():
    reg = Registry()

    @reg.register
    def f(d: date = date(2026, 1, 2)):
        return d

    html = render_index(reg.entries)
    assert 'type="date"' in html
    assert 'value="2026-01-02"' in html
