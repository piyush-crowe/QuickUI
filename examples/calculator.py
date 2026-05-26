"""Multiple registered functions appear as separate cards."""

import instantui


@instantui.app
def add(a: float, b: float) -> float:
    """Sum of two numbers."""
    return a + b


@instantui.app
def divide(a: float, b: float = 1.0) -> float:
    """``a / b`` — try b=0 to see the error card."""
    return a / b


@instantui.app
def stats(numbers: str = "1,2,3,4") -> dict:
    """Mean / min / max of a comma-separated list."""
    xs = [float(x) for x in numbers.split(",") if x.strip()]
    return {"count": len(xs), "min": min(xs), "max": max(xs), "mean": sum(xs) / len(xs)}


if __name__ == "__main__":
    instantui.run(title="Calculator")
