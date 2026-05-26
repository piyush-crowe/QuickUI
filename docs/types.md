# Types reference

One page covering every input control and every output renderer.

## Inputs

The parameter annotation on your decorated function picks the input control.

### `str` — text input

```python
@instantui.app
def fn(name: str = "world"): ...
```

### `int` / `float` — number input

```python
@instantui.app
def fn(count: int = 1, ratio: float = 0.5): ...
```

`float` gets `step="any"` so any decimal works.

### `bool` — checkbox

```python
@instantui.app
def fn(shout: bool = False): ...
```

### `datetime.date` — native date picker

```python
from datetime import date

@instantui.app
def fn(d: date = date(2026, 1, 1)): ...
```

### `datetime.datetime` — datetime-local picker

```python
from datetime import datetime

@instantui.app
def fn(when: datetime): ...
```

The HTML `datetime-local` widget submits `YYYY-MM-DDTHH:MM`; InstantUI casts that back to a `datetime` for you.

### `Literal[...]` — dropdown

```python
from typing import Literal

@instantui.app
def fn(mode: Literal["fast", "balanced", "slow"] = "balanced"): ...
```

The selected option is passed back as the same value that appeared in the `Literal` (preserving non-string types).

### `Enum` subclass — dropdown

```python
from enum import Enum

class Priority(Enum):
    low = 1
    medium = 2
    high = 3

@instantui.app
def fn(p: Priority = Priority.medium): ...
```

Lookup is by member name; falling back to value if the name doesn't match.

### `Annotated[str, Multiline]` — textarea

```python
from typing import Annotated
from instantui import Multiline

@instantui.app
def fn(body: Annotated[str, Multiline] = ""): ...
```

Renders as a resizable textarea (4 rows by default). Underlying type is still `str`.

### Unannotated parameters

Treated as `str`. Defaults still work.

---

## Outputs

Whatever you return is rendered automatically. Wrap returns in one of the type marker classes (`Markdown`, `HTML`, `Image`) to override the default rendering.

### `str`, `int`, `float`, `bool`, `None` — plain text

```python
return "ok"
return 42
```

### `dict` / `list` — pretty-printed JSON

```python
return {"status": "ok", "count": 3}
```

Strings inside dicts with non-JSON-serializable values (dates, enums) are coerced through `str(...)`.

### `list[dict]` — HTML table

```python
return [
    {"name": "alice", "score": 90},
    {"name": "bob",   "score": 85},
]
```

Columns are the union of all keys across rows, preserving first-seen order.

### `pandas.DataFrame` — HTML table

```python
import pandas as pd
return pd.DataFrame({"a": [1, 2], "b": [3, 4]})
```

`pandas` is auto-detected at runtime; it is not a required dependency.

### `instantui.Markdown` — rendered markdown

```python
from instantui import Markdown

return Markdown("## Title\n\n- bullet\n- bullet\n\n```python\nprint('hi')\n```")
```

The built-in renderer supports headings, paragraphs, fenced code blocks, inline code, bold/italic, links, and bullet lists.

### `instantui.HTML` — raw HTML, escape-free

```python
from instantui import HTML

return HTML("<div style='padding:8px'>raw</div>")
```

The string is inserted into the page verbatim. Only return this with content you trust.

### `instantui.Image` — inline image

Accepts `bytes`, a `str` / `pathlib.Path` to a file, or a `PIL.Image.Image` (Pillow is auto-detected, not required).

```python
from instantui import Image

return Image(b"<png bytes>", format="png")
return Image("/tmp/chart.png")
return Image(pil_image, format="jpeg")
```

### `pathlib.Path` — file download or inline image

```python
from pathlib import Path
return Path("/tmp/report.pdf")
```

If the file's MIME type is an image, it renders inline. Otherwise it's a download chip with the filename.

### Captured stdout

This isn't a return type, but worth knowing: anything written to `stdout` during the call is shown in a separate block above the return value.

### Errors

If the function raises, the response shows a red error block with the exception class, message, and full traceback.
