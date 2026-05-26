"""Registry of functions exposed as InstantUI forms."""

from __future__ import annotations

import inspect
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, Callable

from instantui.core.introspection import Field, describe


@dataclass
class Entry:
    """A single registered function plus the metadata needed to render it."""

    name: str
    fn: Callable[..., Any]
    fields: list[Field]
    doc: str = ""
    kind: str = "form"  # "form" | "chat"


@dataclass
class Registry:
    """Holds the ordered set of registered functions for a single process."""

    entries: list[Entry] = field(default_factory=list)

    def register(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Register ``fn`` as a form-style card and return it unchanged."""
        self.entries.append(
            Entry(
                name=fn.__name__,
                fn=fn,
                fields=describe(fn),
                doc=(fn.__doc__ or "").strip(),
                kind="form",
            )
        )
        return fn

    def register_chat(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Register ``fn`` as a chat-style card.

        The function must accept a ``message`` parameter. It may optionally
        accept ``history``, which receives the prior turns as a list of
        ``{"role": "user" | "assistant", "content": str}`` dicts.
        """
        params = inspect.signature(fn).parameters
        if "message" not in params:
            raise ValueError(
                "@instantui.chat function must have a 'message' parameter"
            )
        self.entries.append(
            Entry(
                name=fn.__name__,
                fn=fn,
                fields=[],
                doc=(fn.__doc__ or "").strip(),
                kind="chat",
            )
        )
        return fn

    def __iter__(self) -> Iterator[Entry]:
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def __getitem__(self, index: int) -> Entry:
        return self.entries[index]

    def clear(self) -> None:
        self.entries.clear()


registry = Registry()


def app(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator: register ``fn`` as a form card on the module-level registry."""
    return registry.register(fn)


def chat(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator: register ``fn`` as a chat card on the module-level registry.

    The function must accept ``message: str`` and may optionally accept
    ``history: list[dict]`` (each dict has ``role`` and ``content`` keys).
    """
    return registry.register_chat(fn)
