"""Chat-style UIs: ``@instantui.chat`` registers a function as a chat card.

The function must take ``message: str`` and may optionally take ``history``
(a list of ``{"role": "user" | "assistant", "content": str}`` dicts).

Run with:
    python examples/chat.py
"""

import random
from datetime import datetime

import instantui


@instantui.chat
def echo_bot(message: str) -> str:
    """Reflects your message back. The simplest possible chat function."""
    return f"You said: **{message}**"


@instantui.chat
def stats_bot(message: str, history: list[dict]) -> str:
    """Reports how many turns we've exchanged so far."""
    user_turns = sum(1 for m in history if m["role"] == "user")
    return (
        f"This is turn **{user_turns + 1}**.\n\n"
        f"You typed `{len(message)}` characters.\n\n"
        f"Server time: {datetime.now().isoformat(timespec='seconds')}"
    )


@instantui.chat
def fortune_bot(message: str) -> str:
    """Returns a random "fortune" — pretend it's an LLM."""
    fortunes = [
        "The bug you're chasing is in the file you haven't opened yet.",
        "A short detour through the docs saves an hour of guessing.",
        "Naming is hard. Renaming is harder. Commit early.",
        "Read the error message. Then read it again.",
    ]
    return f"> {random.choice(fortunes)}\n\n_(you asked: {message})_"


# To wire a real LLM (Anthropic shown), uncomment and pip install anthropic:
#
# from anthropic import Anthropic
# client = Anthropic()
#
# @instantui.chat
# def claude(message: str, history: list[dict]) -> str:
#     msgs = history + [{"role": "user", "content": message}]
#     resp = client.messages.create(
#         model="claude-sonnet-4-6",
#         max_tokens=1024,
#         messages=msgs,
#     )
#     return resp.content[0].text


if __name__ == "__main__":
    instantui.run(title="Chatbots")
