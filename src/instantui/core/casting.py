"""Cast raw form values (strings / JSON primitives) to declared types."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Literal, get_args, get_origin

from instantui.core.introspection import Field
from instantui.exceptions import FieldCastError

_TRUTHY = frozenset({"true", "1", "yes", "on"})


def _cast_enum(value: Any, annotation: Any) -> Any:
    """Resolve ``value`` against a Literal[...] or Enum annotation."""
    s = str(value)

    if get_origin(annotation) is Literal:
        for choice in get_args(annotation):
            if str(choice) == s:
                return choice
        raise FieldCastError(f"{value!r} not in Literal options")

    if isinstance(annotation, type) and issubclass(annotation, Enum):
        # Match by member name first, then by value.
        if s in annotation.__members__:
            return annotation[s]
        for member in annotation:
            if str(member.value) == s:
                return member
        raise FieldCastError(f"{value!r} not a member of {annotation.__name__}")

    return s


def cast_value(value: Any, field: Field) -> Any:
    """Coerce ``value`` to the type declared by ``field``.

    Raises :class:`FieldCastError` on conversion failure.
    """
    t = field.type
    try:
        if t == "int":
            return int(value)
        if t == "float":
            return float(value)
        if t == "bool":
            if isinstance(value, bool):
                return value
            return str(value).strip().lower() in _TRUTHY
        if t == "date":
            if isinstance(value, date) and not isinstance(value, datetime):
                return value
            return date.fromisoformat(str(value))
        if t == "datetime":
            if isinstance(value, datetime):
                return value
            # HTML datetime-local emits "YYYY-MM-DDTHH:MM" — fromisoformat handles it.
            return datetime.fromisoformat(str(value))
        if t == "enum":
            return _cast_enum(value, field.annotation)
        # str and multiline both flow through as text.
        return str(value)
    except FieldCastError:
        raise
    except (TypeError, ValueError) as exc:
        raise FieldCastError(f"cannot cast {value!r} to {t}") from exc
