# CLI

Two ways to start the server:

1. Call `instantui.run()` from your script and `python my_script.py`.
2. Use the `instantui` CLI to run any script that registers functions.

```bash
instantui PATH [--host HOST] [--port PORT] [--title TITLE] [--no-browser]
```

## Flags

| Flag             | Default       | Meaning                                                    |
| ---------------- | ------------- | ---------------------------------------------------------- |
| `PATH`           | (required)    | Python file that decorates one or more functions           |
| `--host`         | `127.0.0.1`   | Bind address                                               |
| `--port`         | `8000`        | Bind port                                                  |
| `--title`        | none          | Page heading; the InstantUI brand mark stays in the nav    |
| `--no-browser`   | off           | Don't auto-open the browser                                |
| `--version`      | —             | Print version and exit                                     |

## How it works

The CLI loads the script with `runpy.run_path(...)`, which executes the file with `__name__ == "__main__"`. Top-level `@instantui.app` and `@instantui.chat` decorators run at import time and register functions on the global registry. Then `instantui.run()` is called with the flags you passed.

If your script has its own `if __name__ == "__main__": instantui.run()`, that block also fires when the CLI loads it — meaning the server starts twice. To avoid that, either:

- skip the `if __name__ == "__main__"` block in scripts you intend to launch via the CLI, or
- launch them as `python my_script.py` directly.

## Examples

```bash
# Run a single example with a custom title
instantui examples/calculator.py --title "Calc"

# Bind to all interfaces on a non-standard port
instantui examples/showcase.py --host 0.0.0.0 --port 8080

# Run headless (CI, container, etc.)
instantui examples/hello.py --no-browser
```

## Programmatic equivalent

Everything the CLI does is also available as `instantui.run(...)`. The CLI is for the case where the script doesn't already call `run()`, or you want to override settings without editing the script.
