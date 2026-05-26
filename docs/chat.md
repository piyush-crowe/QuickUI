# Chat — `@instantui.chat`

`@instantui.chat` turns a function into a chat panel: scrollable message log, input box with Send button, animated typing indicator. Each registered chat is one card.

```python
import instantui

@instantui.chat
def echo(message: str) -> str:
    return f"you said: {message}"

instantui.run(title="My bot")
```

## Function signature

The minimum is one parameter:

```python
@instantui.chat
def fn(message: str) -> str: ...
```

If you also declare `history`, you receive the prior turns:

```python
@instantui.chat
def fn(message: str, history: list[dict]) -> str: ...
```

`history` is a list of `{"role": "user" | "assistant", "content": str}` dicts — the same shape OpenAI and Anthropic SDKs use, so you can pass it straight to a model.

The function **must** have a parameter named `message`. Registration fails with `ValueError` otherwise.

## Where history lives

History is held in the browser and re-sent on every turn. The server is stateless:

- No sessions, no auth, no database.
- Page refresh = new conversation.
- Multiple chat cards on one page = independent histories.

If you need durable history, wrap your function with your own persistence layer; the framework doesn't impose one.

## Replies render as Markdown by default

If your function returns a plain `str`, the reply is rendered as Markdown — so `**bold**`, fenced code blocks, links, and bullet lists all work without extra wrapping.

```python
@instantui.chat
def fortune(message: str) -> str:
    return (
        "**Today's fortune**\n\n"
        "- read the error message\n"
        "- then read it again\n\n"
        "```python\nprint('ok')\n```"
    )
```

To bypass Markdown rendering, return one of the wrapper types from [Types reference](types.md):

```python
from instantui import HTML, Image

@instantui.chat
def show_html(message: str) -> HTML:
    return HTML("<div style='padding:8px'>raw</div>")

@instantui.chat
def show_image(message: str) -> Image:
    return Image(generate_png(message), format="png")
```

## Wiring a real LLM

The function body is the only thing that changes; the UI is identical.

### Anthropic

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

### OpenAI

```python
from openai import OpenAI
client = OpenAI()

@instantui.chat
def gpt(message: str, history: list[dict]) -> str:
    msgs = history + [{"role": "user", "content": message}]
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs)
    return resp.choices[0].message.content
```

Neither SDK is required by InstantUI — install only what you use.

## Multiple bots on one page

Register more than one chat function. They appear as separate cards, each with its own history.

```python
@instantui.chat
def claude(message: str, history: list[dict]) -> str: ...

@instantui.chat
def gpt(message: str, history: list[dict]) -> str: ...

@instantui.chat
def echo(message: str) -> str: return message

instantui.run(title="Compare")
```

## Keyboard

- **Enter** — send
- **Shift + Enter** — newline in the input

## Limitations (today)

- **No streaming yet.** Responses are returned in one shot. A streaming mode (function `yield`s tokens, frontend renders the typing animation) is on the roadmap; the decorator and UI contract won't change.
- **No file uploads in the chat input.** Use a form card with a file-typed parameter for now.
- **History is client-side only.** Refresh loses it. Bring your own persistence if you need durability.

## See also

- [examples/chat.py](../examples/chat.py) — three working bots plus the LLM snippet
- [Forms](forms.md) — for parameterized one-shot functions instead of chat
