# Architecture

A short tour of how InstantUI is put together. Useful if you want to extend it, contribute, or just satisfy your curiosity.

## Package layout

```
src/instantui/
├── __init__.py        public API: app, chat, run, registry, version, wrappers
├── _version.py        single source of truth for __version__
├── cli.py             instantui PATH [--flags]
├── exceptions.py      InstantUIError and subclasses
├── types.py           Markdown · HTML · Image · Multiline (wrappers)
├── output.py          render_result(value) -> {kind, value}
├── core/
│   ├── registry.py    Entry, Registry, app(), chat()
│   ├── introspection.py    parameters → Field metadata
│   └── casting.py     incoming JSON → typed kwargs
├── server/
│   ├── handler.py     make_handler(registry, *, title) -> BaseHTTPRequestHandler
│   └── runner.py      run(host, port, *, title, open_browser, registry)
└── rendering/
    ├── renderer.py    render_index(entries, *, title)
    ├── templates/
    │   └── index.html
    └── static/
        ├── style.css
        └── app.js
```

Each subpackage has a single job and can be exercised independently:

- `core` is pure-Python and side-effect-free.
- `rendering` turns entries into HTML and serves static asset bytes; it never touches the network.
- `server` owns `http.server` and routes requests; it depends on `core`, `rendering`, and `output` but nothing else.
- `cli` is a thin argparse wrapper.

## Two kinds of entry

Both decorators land on the same `Registry`. They differ by `Entry.kind`:

```python
@dataclass
class Entry:
    name: str
    fn: Callable[..., Any]
    fields: list[Field]   # empty for chat
    doc: str
    kind: str             # "form" | "chat"
```

The renderer dispatches on `kind` to emit either a form card or a chat card. The handler dispatches on `kind` to choose between `/run/<idx>` and `/chat/<idx>`. Cross-routing is rejected (404).

## Form request flow

```
POST /run/<idx>
    │
    ▼
handler._dispatch_run
    │  read JSON body
    │  cast_value(payload[name], field)  for each declared parameter
    ▼
entry.fn(**kwargs)  with stdout captured
    │
    ▼
render_result(returned_value)   →   {"kind": "...", "value": ...}
    │
    ▼
response: {ok: true, result: <block>, stdout: <captured>}
```

If the call raises, the response is `{ok: false, error: <type>: <msg>\n<traceback>}`.

## Chat request flow

```
POST /chat/<idx>
    │
    ▼
handler._dispatch_chat
    │  read JSON body: {message, history}
    │  inspect signature; pass history only if declared
    ▼
entry.fn(message=..., history=...)
    │
    ▼
plain str?  wrap in Markdown
            │
            ▼
render_result(value)
    │
    ▼
response: {ok: true, reply: <block>}
```

History is sent by the browser and **echoed back** as is — the server keeps no per-conversation state.

## Field metadata

`introspection.describe(fn)` produces a `list[Field]`:

```python
@dataclass(frozen=True)
class Field:
    name: str
    type: str            # int | float | bool | str | date | datetime | enum | multiline
    default: Any
    required: bool
    options: tuple[str, ...]    # populated for "enum"
    annotation: Any             # original annotation, for casting back
```

Why `annotation` is kept: `Enum` and `Literal[...]` need it at cast time to map the submitted string back to the right Python object.

## Output block shape

Everything the server sends back to the browser for a result is one of:

```js
{ kind: "text",     value: "string" }
{ kind: "json",     value: "{...indented JSON...}" }
{ kind: "markdown", value: "## markdown source" }
{ kind: "html",     value: "<raw HTML>" }
{ kind: "image",    value: { mime: "image/png", data_url: "data:image/png;base64,…" } }
{ kind: "file",     value: { name, mime, data_url, is_image } }
{ kind: "table",    value: { columns: [str], rows: [[str]] } }
```

`render_result` is the single dispatch point. To support a new rich output type, add an `isinstance` branch there and add a `case` to `renderBlock` in `app.js`.

## Zero runtime dependencies

The server is pure stdlib `http.server`. Pillow and pandas are imported only if installed — both are detected lazily inside `types.py` / `output.py` and never required.

Dev-only tooling (pytest, ruff, mypy) lives under `[project.optional-dependencies] dev` in `pyproject.toml`.

## Extension points

A few places you can plug in:

- **New input control** — add a branch to `introspection._classify`, a branch to `casting.cast_value`, and a branch to `rendering.renderer._render_input`.
- **New output renderer** — add a branch to `output.render_result` and a `case` to `app.js` `renderBlock`.
- **Custom server config** — `instantui.run(..., registry=my_registry)` lets you mount a registry other than the module-level default. Useful for tests and for hosting multiple isolated apps in one process.

## Test surface

```
tests/
├── test_casting.py        cast_value across types
├── test_introspection.py  describe() metadata
├── test_registry.py       app() / chat() decorators
├── test_rendering.py      HTML output for both card kinds
├── test_output.py         render_result block shapes
├── test_chat.py           /chat/<idx> live endpoint
└── test_server.py         /run/<idx> live endpoint
```

`conftest.py` resets the module-level registry between tests so test cases stay isolated.
