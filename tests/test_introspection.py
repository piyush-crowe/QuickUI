from datetime import date, datetime
from enum import Enum
from typing import Annotated, Literal

from instantui.core.introspection import describe, type_name
from instantui.types import Multiline


def test_type_name_primitives():
    assert type_name(int) == "int"
    assert type_name(float) == "float"
    assert type_name(bool) == "bool"
    assert type_name(str) == "str"


def test_type_name_unknown_falls_back_to_str():
    assert type_name(list) == "str"


def test_describe_extracts_basic_fields():
    def greet(name: str, times: int = 1, loud: bool = False):
        return name

    fields = describe(greet)
    assert [(f.name, f.type, f.default, f.required) for f in fields] == [
        ("name", "str", None, True),
        ("times", "int", 1, False),
        ("loud", "bool", False, False),
    ]


def test_describe_missing_annotation_defaults_to_str():
    def f(x):
        return x

    [field] = describe(f)
    assert field.type == "str"
    assert field.required is True


def test_describe_date_and_datetime():
    def f(d: date, t: datetime):
        return d

    fields = describe(f)
    assert [f.type for f in fields] == ["date", "datetime"]


def test_describe_literal_options():
    def f(mode: Literal["fast", "slow"] = "fast"):
        return mode

    [field] = describe(f)
    assert field.type == "enum"
    assert field.options == ("fast", "slow")
    assert field.default == "fast"


def test_describe_enum_class_options():
    class Color(Enum):
        red = "r"
        blue = "b"

    def f(c: Color = Color.red):
        return c

    [field] = describe(f)
    assert field.type == "enum"
    assert field.options == ("red", "blue")


def test_describe_annotated_multiline():
    def f(body: Annotated[str, Multiline] = ""):
        return body

    [field] = describe(f)
    assert field.type == "multiline"
