"""Convert a function's return value into a typed block for the frontend."""

from __future__ import annotations

import base64
import json
import mimetypes
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from instantui.types import HTML, Image, Markdown

_IMAGE_MIMES = {"image/png", "image/jpeg", "image/gif", "image/webp", "image/svg+xml"}


def _has_pandas_dataframe(value: Any) -> bool:
    return type(value).__module__.startswith("pandas") and type(value).__name__ == "DataFrame"


def _dataframe_to_table(df: Any) -> dict[str, Any]:
    columns = [str(c) for c in df.columns]
    rows = df.astype(object).where(df.notna(), None).values.tolist()
    return {"columns": columns, "rows": [[_to_cell(v) for v in row] for row in rows]}


def _list_of_dicts_to_table(rows: list[dict]) -> dict[str, Any]:
    columns: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                columns.append(str(key))
    body = [[_to_cell(row.get(c)) for c in columns] for row in rows]
    return {"columns": columns, "rows": body}


def _to_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return str(value)


def _path_block(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    mime, _ = mimetypes.guess_type(path.name)
    mime = mime or "application/octet-stream"
    data_url = f"data:{mime};base64," + base64.b64encode(data).decode("ascii")
    return {
        "kind": "file",
        "value": {
            "name": path.name,
            "mime": mime,
            "data_url": data_url,
            "is_image": mime in _IMAGE_MIMES,
        },
    }


def _image_block(img: Image) -> dict[str, Any]:
    mime = f"image/{img.format}"
    data_url = f"data:{mime};base64," + base64.b64encode(img.bytes).decode("ascii")
    return {"kind": "image", "value": {"mime": mime, "data_url": data_url}}


def _json_default(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.name
    return str(value)


def render_result(value: Any) -> dict[str, Any]:
    """Convert a function return value to a ``{"kind", "value"}`` block."""
    if value is None:
        return {"kind": "text", "value": ""}
    if isinstance(value, Markdown):
        return {"kind": "markdown", "value": str(value)}
    if isinstance(value, HTML):
        return {"kind": "html", "value": str(value)}
    if isinstance(value, Image):
        return _image_block(value)
    if isinstance(value, Path):
        return _path_block(value)
    if _has_pandas_dataframe(value):
        return {"kind": "table", "value": _dataframe_to_table(value)}
    if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
        return {"kind": "table", "value": _list_of_dicts_to_table(value)}
    if isinstance(value, (dict, list)):
        return {"kind": "json", "value": json.dumps(value, indent=2, default=_json_default)}
    if isinstance(value, (date, datetime)):
        return {"kind": "text", "value": value.isoformat()}
    if isinstance(value, Enum):
        return {"kind": "text", "value": f"{type(value).__name__}.{value.name}"}
    return {"kind": "text", "value": str(value)}
