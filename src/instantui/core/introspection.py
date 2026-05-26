"""Introspect a callable's signature and describe its parameters as form fields."""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from dataclasses import field as dc_field
from datetime import date, datetime
from enum import Enum
from typing import Any, Callable, Literal, get_args, get_origin, get_type_hints

from instantui.types import Multiline, _MultilineSentinel

_PRIMITIVE_NAMES: dict[type, str] = {
    int: "int",
    float: "float",
    bool: "bool",
    str: "str",
    date: "date",
    datetime: "datetime",
}


@dataclass(frozen=True)
class Field:
    """A single input field derived from a function parameter."""

    name: str
    type: str
    default: Any = None
    required: bool = True
    options: tuple[str, ...] = ()
    annotation: Any = dc_field(default=None, compare=False)


def _classify(annotation: Any) -> tuple[str, tuple[str, ...]]:
    """Return ``(type_name, options)`` for an annotation."""
    origin = get_origin(annotation)

    # Literal[...] -> enum
    if origin is Literal:
        return "enum", tuple(str(a) for a in get_args(annotation))

    # Annotated[T, ...] -> unwrap, but honour the Multiline marker
    if origin is not None and getattr(annotation, "__metadata__", None) is not None:
        base = get_args(annotation)[0]
        meta = annotation.__metadata__
        if any(isinstance(m, _MultilineSentinel) or m is Multiline for m in meta):
            return "multiline", ()
        return _classify(base)

    # Enum subclass -> enum
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return "enum", tuple(m.name for m in annotation)

    return _PRIMITIVE_NAMES.get(annotation, "str"), ()


def type_name(annotation: Any) -> str:
    """Map a type annotation to its rendered type name."""
    return _classify(annotation)[0]


def describe(fn: Callable[..., Any]) -> list[Field]:
    """Inspect ``fn`` and return one :class:`Field` per parameter."""
    sig = inspect.signature(fn)
    try:
        hints = get_type_hints(fn, include_extras=True)
    except Exception:  # noqa: BLE001 - unresolved hints fall back to raw annotations
        hints = {}

    fields: list[Field] = []
    for name, param in sig.parameters.items():
        annotation = hints.get(
            name,
            param.annotation if param.annotation is not inspect.Parameter.empty else str,
        )
        kind, options = _classify(annotation)
        has_default = param.default is not inspect.Parameter.empty
        fields.append(
            Field(
                name=name,
                type=kind,
                default=param.default if has_default else None,
                required=not has_default,
                options=options,
                annotation=annotation,
            )
        )
    return fields
