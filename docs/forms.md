# Forms — `@instantui.app`

`@instantui.app` turns a parameterized function into a form card: each parameter becomes an input, the function body runs on submit, and the return value is rendered below.

```python
import instantui

@instantui.app
def add(a: int, b: int = 1) -> int:
    """Sum two numbers."""
    return a + b

instantui.run()
```

## Inputs are driven by type annotations

The annotation on each parameter picks the input control. Defaults are pre-filled, unannotated parameters fall back to `str`.

```python
from datetime import date
from typing import Annotated, Literal
from instantui import Multiline

@instantui.app
def report(
    title: str,                                       # text input
    count: int = 10,                                  # number input
    threshold: float = 0.5,                           # number, step=any
    enabled: bool = True,                             # checkbox
    mode: Literal["fast", "slow"] = "fast",           # dropdown
    when: date = date(2026, 1, 1),                    # date picker
    notes: Annotated[str, Multiline] = "",            # textarea
) -> str:
    ...
```

See [Types reference](types.md) for the full table.

## Docstring shows up in the UI

The first paragraph of the function's docstring is rendered under the card title.

```python
@instantui.app
def divide(a: float, b: float = 1.0) -> float:
    """``a / b`` — try b=0 to see the error card."""
    return a / b
```

## Outputs are auto-rendered

You return values; the UI figures out how to show them.

| Return                                          | Rendered as           |
| ----------------------------------------------- | --------------------- |
| `str`, `int`, `float`, `bool`, `None`           | plain text            |
| `dict` / `list`                                 | pretty-printed JSON   |
| `list[dict]`                                    | HTML table            |
| `pandas.DataFrame`                              | HTML table            |
| `instantui.Markdown(...)`                       | rendered markdown     |
| `instantui.HTML(...)`                           | raw HTML              |
| `instantui.Image(bytes \| path \| PIL.Image)`   | inline image          |
| `pathlib.Path`                                  | inline image or download |

Full reference in [Types reference](types.md).

## Captured stdout

Anything written to `stdout` during the call is shown above the return value, in its own block.

```python
@instantui.app
def loud(name: str) -> str:
    print("about to greet…")
    return f"hi {name}"
```

## Errors

If the function raises, the response shows a red block with the exception class, message, and full traceback. The card stays usable.

## Multiple cards

Decorate as many functions as you like — they all become cards on the same page, in definition order.

```python
@instantui.app
def add(a: int, b: int) -> int: return a + b

@instantui.app
def mul(a: int, b: int) -> int: return a * b
```

## Calling the function directly still works

`@instantui.app` returns the original function unchanged. You can still import and call it from regular code, write unit tests against it, etc.

```python
@instantui.app
def add(a: int, b: int) -> int: return a + b

assert add(2, 3) == 5
```
