import base64
import json
from datetime import date, datetime
from pathlib import Path

from instantui import HTML, Image, Markdown
from instantui.output import render_result


def test_text_block():
    block = render_result("hello")
    assert block == {"kind": "text", "value": "hello"}


def test_none_block():
    assert render_result(None) == {"kind": "text", "value": ""}


def test_markdown_wrapper():
    block = render_result(Markdown("# hi"))
    assert block == {"kind": "markdown", "value": "# hi"}


def test_html_wrapper():
    block = render_result(HTML("<b>x</b>"))
    assert block == {"kind": "html", "value": "<b>x</b>"}


def test_dict_renders_as_json():
    block = render_result({"a": 1})
    assert block["kind"] == "json"
    assert json.loads(block["value"]) == {"a": 1}


def test_list_of_dicts_renders_as_table():
    block = render_result([{"a": 1, "b": 2}, {"a": 3, "b": 4}])
    assert block["kind"] == "table"
    assert block["value"]["columns"] == ["a", "b"]
    assert block["value"]["rows"] == [["1", "2"], ["3", "4"]]


def test_image_block_encodes_bytes():
    payload = b"\x89PNGfakebytes"
    block = render_result(Image(payload, format="png"))
    assert block["kind"] == "image"
    expected = "data:image/png;base64," + base64.b64encode(payload).decode()
    assert block["value"]["data_url"] == expected


def test_path_block_inline_image(tmp_path: Path):
    p = tmp_path / "x.png"
    p.write_bytes(b"\x89PNG\r\n")
    block = render_result(p)
    assert block["kind"] == "file"
    assert block["value"]["is_image"] is True
    assert block["value"]["mime"] == "image/png"


def test_path_block_other_files(tmp_path: Path):
    p = tmp_path / "notes.txt"
    p.write_text("hi")
    block = render_result(p)
    assert block["kind"] == "file"
    assert block["value"]["is_image"] is False


def test_date_and_datetime_render_as_text():
    assert render_result(date(2026, 1, 2)) == {"kind": "text", "value": "2026-01-02"}
    assert render_result(datetime(2026, 1, 2, 15, 30)) == {
        "kind": "text",
        "value": "2026-01-02T15:30:00",
    }
