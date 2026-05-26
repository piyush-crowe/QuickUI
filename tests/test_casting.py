from datetime import date, datetime
from enum import Enum
from typing import Literal

import pytest

from instantui.core.casting import cast_value
from instantui.core.introspection import Field, describe
from instantui.exceptions import FieldCastError


def _field(name: str, type_: str, annotation=None, options=()) -> Field:
    return Field(name=name, type=type_, annotation=annotation, options=options)


def test_cast_int():
    assert cast_value("42", _field("x", "int")) == 42


def test_cast_float():
    assert cast_value("3.14", _field("x", "float")) == 3.14


def test_cast_bool_truthy_strings():
    f = _field("x", "bool")
    for v in ("true", "1", "yes", "on", "TRUE"):
        assert cast_value(v, f) is True


def test_cast_bool_falsy_strings():
    f = _field("x", "bool")
    for v in ("false", "0", "no", "off", ""):
        assert cast_value(v, f) is False


def test_cast_str_passthrough():
    assert cast_value(123, _field("x", "str")) == "123"


def test_cast_invalid_int_raises():
    with pytest.raises(FieldCastError):
        cast_value("nope", _field("x", "int"))


def test_cast_date():
    f = _field("x", "date")
    assert cast_value("2026-01-02", f) == date(2026, 1, 2)


def test_cast_datetime_local_format():
    f = _field("x", "datetime")
    # The HTML datetime-local widget emits this shape.
    assert cast_value("2026-01-02T15:30", f) == datetime(2026, 1, 2, 15, 30)


def test_cast_enum_literal():
    def f(mode: Literal["fast", "slow"] = "fast"):
        return mode

    [field] = describe(f)
    assert cast_value("slow", field) == "slow"
    with pytest.raises(FieldCastError):
        cast_value("medium", field)


def test_cast_enum_class():
    class Color(Enum):
        red = "r"
        blue = "b"

    def f(c: Color = Color.red):
        return c

    [field] = describe(f)
    assert cast_value("blue", field) is Color.blue
    # Lookup by value also works.
    assert cast_value("r", field) is Color.red
