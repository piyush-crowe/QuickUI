# Usage

## The decorator

`@instantui.app` registers a function in the module-level `registry`. Repeated decoration adds more cards.

```python
import instantui

@instantui.app
def add(a: int, b: int) -> int:
    return a + b
```

## Starting the server

```python
instantui.run(host="127.0.0.1", port=8000, open_browser=True)
```

`run()` blocks until interrupted. Pass `registry=` to use a custom `Registry` instead of the module-level one (useful for tests).

## CLI

```
instantui PATH [--host HOST] [--port PORT] [--no-browser]
```

The script is loaded with `runpy.run_path`, so any top-level `@instantui.app` decorator runs at import time.

## Type → input mapping

| Annotation | HTML input        | Casting           |
|------------|-------------------|-------------------|
| `str`      | `type="text"`     | `str(value)`      |
| `int`      | `type="number"`   | `int(value)`      |
| `float`    | `type="number"`   | `float(value)`    |
| `bool`     | `type="checkbox"` | truthy-string set |

Unknown annotations fall back to `str`.

## Output

The return value is rendered as text (`str(result)`), except `dict`/`list`, which are pretty-printed as JSON. Any text written to stdout during the call is shown in a separate block above the return value.

## Errors

If the function raises, the response contains the exception class, message, and full traceback, rendered in the red error block.
