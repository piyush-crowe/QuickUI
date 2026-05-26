"""Demonstrates the new input and output types.

Run with:
    python examples/showcase.py
"""

import struct
import zlib
from datetime import date, datetime
from enum import Enum
from typing import Annotated, Literal

import instantui
from instantui import HTML, Markdown, Multiline

# ---------- inputs -----------------------------------------------------------


class Priority(Enum):
    low = 1
    medium = 2
    high = 3


@instantui.app
def choose_mode(mode: Literal["fast", "balanced", "thorough"] = "balanced") -> str:
    """Literal[...] becomes a dropdown."""
    return f"running in {mode} mode"


@instantui.app
def pick_priority(p: Priority = Priority.medium) -> str:
    """Enum subclasses also become dropdowns."""
    return f"priority is {p.name} (value={p.value})"


@instantui.app
def days_between(start: date, end: date = date(2026, 12, 31)) -> str:
    """``date`` annotations render as native date pickers."""
    return f"{(end - start).days} days"


@instantui.app
def remind_at(when: datetime) -> str:
    """``datetime`` annotations render as datetime-local pickers."""
    return f"reminder set for {when.isoformat()}"


@instantui.app
def echo_note(body: Annotated[str, Multiline] = "type something\non multiple lines") -> str:
    """``Annotated[str, Multiline]`` becomes a textarea."""
    return body


# ---------- outputs ----------------------------------------------------------


@instantui.app
def render_markdown(topic: str = "InstantUI") -> Markdown:
    """Return Markdown(...) and it gets rendered, not displayed as text."""
    return Markdown(
        f"## About **{topic}**\n\n"
        "- Decorate any function with `@instantui.app`\n"
        "- Types drive the inputs\n"
        "- Wrap returns in `Markdown`, `HTML`, or `Image`\n\n"
        "```python\n@instantui.app\ndef hello(name: str) -> str:\n    return f'hi {name}'\n```"
    )


@instantui.app
def render_html() -> HTML:
    """HTML(...) bypasses escaping — only use for content you trust."""
    return HTML(
        '<div style="padding:12px;background:#eef;border-radius:6px">'
        "Arbitrary <b>inline</b> HTML.</div>"
    )


@instantui.app
def people_table(rows: int = 3) -> list[dict]:
    """A list of dicts renders as a table automatically."""
    return [
        {"id": i, "name": f"user{i}", "score": i * 10}
        for i in range(1, rows + 1)
    ]


def _gradient_png(width: int = 120, height: int = 120) -> bytes:
    """Build a small RGB PNG without any third-party libraries."""
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # PNG filter byte per scanline
        for x in range(width):
            raw.append((x * 255) // (width - 1))      # R: left -> right
            raw.append((y * 255) // (height - 1))     # G: top  -> bottom
            raw.append(((x ^ y) * 255 // max(width, height)) & 0xFF)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(
            ">I", zlib.crc32(tag + data)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw)))
        + chunk(b"IEND", b"")
    )


@instantui.app
def gradient(size: int = 120) -> instantui.Image:
    """Return an ``Image(...)`` and it's rendered inline."""
    return instantui.Image(_gradient_png(size, size), format="png")


if __name__ == "__main__":
    instantui.run(title="Showcase")
