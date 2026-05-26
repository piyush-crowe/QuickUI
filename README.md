# InstantUI

> Wrap a Python function with a decorator and get an instant web UI. Zero runtime dependencies.

```python
import instantui

@instantui.app
def greet(name: str = "world", times: int = 1, shout: bool = False) -> str:
    """Greet someone a few times."""
    msg = " ".join([f"Hello {name}!"] * times)
    return msg.upper() if shout else msg

if __name__ == "__main__":
    instantui.run(title="Hello")
```

Run it, open http://127.0.0.1:8000, and you get a form per function — typed inputs, captured stdout, and a return value rendered as text, JSON, markdown, an image, or a table depending on what you return.

## Install

```bash
pip install instantui
```

## Two flavors of card

### Form cards — `@instantui.app`

A parameterized function turns into a form. Submit it and you see the return value.

```python
@instantui.app
def add(a: int, b: int = 1) -> int:
    return a + b
```

### Chat cards — `@instantui.chat`

A function with a `message` parameter (and optionally `history`) turns into a chat panel — message log, input box, typing indicator. History is held in the browser and re-sent on each turn, so the server stays stateless.

```python
@instantui.chat
def my_bot(message: str, history: list[dict]) -> str:
    # history items look like {"role": "user" | "assistant", "content": str}
    return f"echo: {message}"
```

`history` matches the OpenAI/Anthropic message shape, so you can pass it straight to an LLM SDK — see [examples/chat.py](examples/chat.py) for a sketch.

Form and chat cards can live on the same page.

## Inputs

| Annotation                         | Rendered as                  |
| ---------------------------------- | ---------------------------- |
| `str`                              | text input                   |
| `int`                              | number input                 |
| `float`                            | number input, `step=any`     |
| `bool`                             | checkbox                     |
| `datetime.date`                    | native date picker           |
| `datetime.datetime`                | datetime-local picker        |
| `Literal["a", "b"]`                | dropdown                     |
| `Enum` subclass                    | dropdown                     |
| `Annotated[str, instantui.Multiline]` | textarea                  |

Unannotated parameters fall back to `str`. Defaults are pre-filled in the form.

## Outputs

Whatever you return is auto-rendered. Wrappers let you opt into richer rendering.

| Return value                                  | Rendered as                            |
| --------------------------------------------- | -------------------------------------- |
| `str`, `int`, `float`, `bool`, `None`         | plain text                             |
| `dict`, `list`                                | pretty-printed JSON                    |
| `list[dict]`                                  | HTML table                             |
| `pandas.DataFrame`                            | HTML table (auto-detected, no hard dep)|
| `instantui.Markdown("…")`                     | rendered markdown                      |
| `instantui.HTML("…")`                         | raw HTML (escape-free, opt-in)         |
| `instantui.Image(bytes \| path \| PIL.Image)` | inline image                           |
| `pathlib.Path`                                | download link (or inline if an image)  |
| an exception                                  | red error block with traceback         |

Anything written to `stdout` during the call is shown in a separate block above the return value.

## Customizing the page

```python
instantui.run(host="127.0.0.1", port=8000, title="My App", open_browser=True)
```

`title` is shown as the page heading. The small "InstantUI" brand mark stays in the top-left nav regardless.

## CLI

```bash
instantui PATH [--host HOST] [--port PORT] [--title TITLE] [--no-browser]
```

The script is loaded with `runpy.run_path`, so any top-level `@instantui.app` / `@instantui.chat` decorator runs at import time.

```bash
instantui examples/calculator.py --port 8080 --title "Calc"
```

## Documentation

Full docs live under [`docs/`](docs/README.md):

- [Getting started](docs/getting-started.md)
- [Forms — `@instantui.app`](docs/forms.md)
- [Chat — `@instantui.chat`](docs/chat.md)
- [Types reference](docs/types.md) (every input + output type)
- [CLI](docs/cli.md)
- [Architecture](docs/architecture.md)

## Examples

- [`examples/hello.py`](examples/hello.py) — minimal form
- [`examples/calculator.py`](examples/calculator.py) — multiple form cards
- [`examples/showcase.py`](examples/showcase.py) — every input + output type
- [`examples/chat.py`](examples/chat.py) — three chat bots, with an Anthropic snippet to wire a real LLM

## Project layout

```
src/instantui/
├── core/         registry · introspection · casting
├── server/       BaseHTTPRequestHandler · runner
├── rendering/    HTML renderer · templates/ · static/
├── output.py     return-value → typed block
├── types.py      Markdown · HTML · Image · Multiline
├── cli.py        `instantui script.py`
└── exceptions.py
```

Each subpackage is independently testable. The HTTP server uses only `http.server` from the standard library; Pillow and pandas are auto-detected at runtime if installed but never required.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
mypy
```

53 tests on Python 3.9 – 3.12, Linux / macOS / Windows in CI.

## Status

Alpha. The `@instantui.app` / `@instantui.chat` / `run()` contract is stable; internals may still move.

## License

[MIT](LICENSE)
