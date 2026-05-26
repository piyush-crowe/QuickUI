"""Render the InstantUI index page and serve static template assets."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime
from html import escape
from importlib import resources

from instantui.core.introspection import Field
from instantui.core.registry import Entry

_TEMPLATE_PKG = "instantui.rendering.templates"
_STATIC_PKG = "instantui.rendering.static"

_STATIC_MIME = {
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}


def _read_template(name: str) -> str:
    return resources.files(_TEMPLATE_PKG).joinpath(name).read_text(encoding="utf-8")


def static_asset(name: str) -> tuple[bytes, str] | None:
    """Return ``(body, content_type)`` for a static asset, or ``None`` if missing."""
    suffix = "." + name.rsplit(".", 1)[-1] if "." in name else ""
    mime = _STATIC_MIME.get(suffix)
    if mime is None:
        return None
    try:
        body = resources.files(_STATIC_PKG).joinpath(name).read_bytes()
    except (FileNotFoundError, ModuleNotFoundError):
        return None
    return body, mime


def _default_str(default: object) -> str:
    if default is None:
        return ""
    if isinstance(default, datetime):
        # HTML datetime-local format: "YYYY-MM-DDTHH:MM"
        return default.strftime("%Y-%m-%dT%H:%M")
    if isinstance(default, date):
        return default.isoformat()
    if hasattr(default, "name") and hasattr(default, "value"):  # Enum
        return default.name
    return str(default)


def _render_input(field: Field) -> str:
    name = escape(field.name, quote=True)
    t = field.type
    default_value = _default_str(field.default)

    if t == "bool":
        checked = " checked" if field.default else ""
        return (
            f'<label class="field field--bool">'
            f'<input type="checkbox" name="{name}"{checked}>'
            f'<span>{name}</span>'
            f"</label>"
        )

    if t == "enum":
        opts = []
        for opt in field.options:
            o = escape(opt, quote=True)
            selected = " selected" if o == escape(default_value, quote=True) else ""
            opts.append(f'<option value="{o}"{selected}>{o}</option>')
        return (
            f'<label class="field">'
            f'<span class="field__name">{name} <em>(enum)</em></span>'
            f'<select name="{name}">{"".join(opts)}</select>'
            f"</label>"
        )

    if t == "multiline":
        return (
            f'<label class="field">'
            f'<span class="field__name">{name} <em>(text)</em></span>'
            f'<textarea name="{name}" rows="4">{escape(default_value)}</textarea>'
            f"</label>"
        )

    if t == "date":
        return _simple_input(name, "date", default_value, t)
    if t == "datetime":
        return _simple_input(name, "datetime-local", default_value, t)

    input_type = "number" if t in ("int", "float") else "text"
    step = ' step="any"' if t == "float" else ""
    return (
        f'<label class="field">'
        f'<span class="field__name">{name} <em>({t})</em></span>'
        f'<input type="{input_type}"{step} name="{name}" '
        f'value="{escape(default_value, quote=True)}">'
        f"</label>"
    )


def _simple_input(name: str, html_type: str, default: str, label_type: str) -> str:
    return (
        f'<label class="field">'
        f'<span class="field__name">{name} <em>({label_type})</em></span>'
        f'<input type="{html_type}" name="{name}" '
        f'value="{escape(default, quote=True)}">'
        f"</label>"
    )


def _card_head(entry: Entry) -> str:
    name = escape(entry.name)
    doc = escape(entry.doc)
    doc_html = f'<p class="card__doc">{doc}</p>' if doc else ""
    return (
        f'<header class="card__head">'
        f'<h2 class="card__title">{name}</h2>'
        f"{doc_html}"
        f"</header>"
    )


def _render_form_card(index: int, entry: Entry) -> str:
    inputs = "".join(_render_input(f) for f in entry.fields)
    return (
        f'<section class="card" data-index="{index}">'
        f"{_card_head(entry)}"
        f'<form class="card__form" data-index="{index}">'
        f'<div class="fields">{inputs}</div>'
        f'<button type="submit" class="run">Run</button>'
        f"</form>"
        f'<div class="out" data-index="{index}" hidden>'
        f'<div class="out__block out__block--stdout" hidden>'
        f'<div class="out__label">stdout</div>'
        f'<pre class="out__pre out__pre--stdout"></pre>'
        f"</div>"
        f'<div class="out__block out__block--result">'
        f'<div class="out__label">return value</div>'
        f'<div class="out__result"></div>'
        f"</div>"
        f"</div>"
        f"</section>"
    )


def _render_chat_card(index: int, entry: Entry) -> str:
    return (
        f'<section class="card card--chat" data-index="{index}">'
        f"{_card_head(entry)}"
        f'<div class="chat" data-index="{index}">'
        f'<div class="chat__log" aria-live="polite"></div>'
        f'<form class="chat__form" data-index="{index}">'
        f'<textarea class="chat__input" name="message" rows="1" '
        f'placeholder="Send a message&hellip;"></textarea>'
        f'<button type="submit" class="chat__send">Send</button>'
        f"</form>"
        f"</div>"
        f"</section>"
    )


def _render_card(index: int, entry: Entry) -> str:
    if entry.kind == "chat":
        return _render_chat_card(index, entry)
    return _render_form_card(index, entry)


def render_index(entries: Iterable[Entry], *, title: str | None = None) -> str:
    """Render the full index HTML for ``entries``.

    If ``title`` is given, it's shown as the page heading. Otherwise only the
    "InstantUI" brand mark appears at the top.
    """
    cards = "\n".join(_render_card(i, e) for i, e in enumerate(entries))
    title_block = (
        f'<h1 class="page__title">{escape(title)}</h1>' if title else ""
    )
    template = _read_template("index.html")
    return template.replace("{{CARDS}}", cards).replace("{{TITLE_BLOCK}}", title_block)
