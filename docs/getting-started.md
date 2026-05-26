# Getting started

## Install

```bash
pip install instantui
```

Requires Python 3.9+.

## Your first form

Create a file:

```python
# hello.py
import instantui

@instantui.app
def greet(name: str = "world", times: int = 1, shout: bool = False) -> str:
    """Greet someone a few times."""
    msg = " ".join([f"Hello {name}!"] * times)
    return msg.upper() if shout else msg

if __name__ == "__main__":
    instantui.run(title="Hello")
```

Run it:

```bash
python hello.py
```

Your browser opens to http://127.0.0.1:8000. You'll see a form with three fields — a text input, a number input, and a checkbox — driven entirely by the type annotations. Click **Run** and the return value appears below.

## Your first chat bot

```python
# bot.py
import instantui

@instantui.chat
def echo(message: str, history: list[dict]) -> str:
    return f"you said **{message}** (turn {len(history) // 2 + 1})"

if __name__ == "__main__":
    instantui.run(title="My bot")
```

A `@instantui.chat` function gets a chat panel — message log, input box, typing indicator. `history` is held in the browser and re-sent on every turn, so the server stays stateless. Replies are rendered as Markdown by default (so `**bold**` works).

To wire a real LLM, the function body is the only thing that changes — the UI stays the same:

```python
from anthropic import Anthropic
client = Anthropic()

@instantui.chat
def claude(message: str, history: list[dict]) -> str:
    msgs = history + [{"role": "user", "content": message}]
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=msgs,
    )
    return resp.content[0].text
```

## Combining cards

A single script can register any mix of `@instantui.app` and `@instantui.chat` functions. They all appear as cards on the same page, in the order they were defined.

```python
@instantui.app
def calc(a: int, b: int) -> int: return a + b

@instantui.chat
def bot(message: str) -> str: return message.upper()

instantui.run(title="Tools")
```

## CLI alternative

Instead of calling `instantui.run()` from your script, you can use the CLI:

```bash
instantui hello.py --port 8080 --title "Hello"
```

The script's `@instantui.app` / `@instantui.chat` decorators run at import time. The CLI then starts the server. See [CLI](cli.md) for all flags.

## Where to go next

- [Forms](forms.md) — every input type, output rendering, error handling
- [Chat](chat.md) — history shape, LLM patterns, multi-bot pages
- [Types reference](types.md) — one-page lookup for every input and output type
- [Architecture](architecture.md) — how it all works under the hood
