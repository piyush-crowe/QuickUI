# InstantUI

> Wrap a Python function with a decorator and get an instant web UI. Zero dependencies.

```python
import instantui

@instantui.app
def greet(name: str = "world", times: int = 1, shout: bool = False) -> str:
    """Greet someone a few times."""
    msg = " ".join([f"Hello {name}!"] * times)
    return msg.upper() if shout else msg

if __name__ == "__main__":
    instantui.run()
```

Run it, open http://127.0.0.1:8000, and you get a form per function — typed inputs, captured stdout, and the return value rendered as JSON when it's a dict or list.

## Install

```bash
pip install instantui
```

## Usage

Decorate any function with `@instantui.app` and call `instantui.run()`:

```bash
python examples/hello.py
```

Or use the CLI to run any script that registers functions:

```bash
instantui examples/calculator.py --port 8080
```

CLI flags: `--host`, `--port`, `--no-browser`, `--version`.

## Supported parameter types

| Annotation | Rendered as       |
|-----------:|-------------------|
| `str`      | text input        |
| `int`      | number input      |
| `float`    | number, step=any  |
| `bool`     | checkbox          |

Unannotated parameters fall back to `str`. Defaults are pre-filled.

## Project layout

```
src/instantui/
├── core/         registry · introspection · casting
├── server/       BaseHTTPRequestHandler · runner
├── rendering/    HTML renderer · templates/ · static/
├── cli.py        `instantui script.py`
└── exceptions.py
```

Each subpackage is independently testable. The HTTP server uses only `http.server` from the standard library.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
mypy
```

## Status

Alpha. The decorator/runner contract is stable; everything else may move.

## License

[MIT](LICENSE)
