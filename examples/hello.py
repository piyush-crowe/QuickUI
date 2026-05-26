"""Minimal example: one function, one form.

Run with:
    instantui examples/hello.py
"""

import instantui


@instantui.app
def greet(name: str = "world", times: int = 1, shout: bool = False) -> str:
    """Greet ``name`` a few times."""
    msg = " ".join([f"Hello {name}!"] * times)
    return msg.upper() if shout else msg


if __name__ == "__main__":
    instantui.run(title="Hello")
