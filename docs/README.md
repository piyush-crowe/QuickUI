# InstantUI documentation

Wrap a Python function with a decorator and get an instant web UI. Zero runtime dependencies.

## Contents

| Page                                       | What's in it                                              |
| ------------------------------------------ | --------------------------------------------------------- |
| [Getting started](getting-started.md)      | Install, first form, first chat, first 5 minutes          |
| [Forms — `@instantui.app`](forms.md)       | Parameterized functions as form cards                     |
| [Chat — `@instantui.chat`](chat.md)        | Functions as chat panels; wiring a real LLM               |
| [Types reference](types.md)                | Every input + output type, in one place                   |
| [CLI](cli.md)                              | `instantui script.py` command                             |
| [Architecture](architecture.md)            | How requests flow; package layout; extension points       |

## At a glance

```python
import instantui

@instantui.app
def add(a: int, b: int = 1) -> int:
    """Sum two numbers."""
    return a + b

@instantui.chat
def echo(message: str) -> str:
    return f"you said: **{message}**"

if __name__ == "__main__":
    instantui.run(title="My tools")
```

Run it, open http://127.0.0.1:8000, and both a form card and a chat card appear on the same page.

## Project status

Alpha. The decorator and `run()` contract are stable; internals may still move.
