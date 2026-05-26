"""Public wrapper types users can return / annotate to influence rendering.

Users import these from the top-level ``instantui`` namespace::

    from instantui import Markdown, HTML, Image, Multiline
"""

from __future__ import annotations

import io as _io
from pathlib import Path
from typing import Any, Union


class Markdown(str):
    """Mark a string as Markdown so the UI renders it formatted."""


class HTML(str):
    """Mark a string as raw HTML so the UI renders it as-is.

    Trust whatever you wrap in this; it bypasses escaping.
    """


class _MultilineSentinel:
    """Marker used inside ``Annotated[str, Multiline]`` to request a textarea."""

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return "Multiline"


Multiline = _MultilineSentinel()


class Image:
    """An image to display in the UI.

    Accepts:
    - ``bytes`` / ``bytearray`` (image bytes)
    - ``str`` / :class:`pathlib.Path` (file path)
    - ``PIL.Image.Image`` (if Pillow is installed)
    """

    def __init__(self, source: Any, format: str = "png") -> None:  # noqa: A002
        self.format = format.lower()
        self.bytes = self._to_bytes(source)

    def _to_bytes(self, source: Any) -> bytes:
        if isinstance(source, (bytes, bytearray)):
            return bytes(source)
        if isinstance(source, (str, Path)):
            return Path(source).read_bytes()
        # Pillow path — kept optional.
        try:
            from PIL.Image import Image as _PILImage  # noqa: PLC0415
        except ImportError:
            _PILImage = None  # type: ignore[assignment]
        if _PILImage is not None and isinstance(source, _PILImage):
            buf = _io.BytesIO()
            source.save(buf, format=self.format.upper())
            return buf.getvalue()
        raise TypeError(
            "Image expected bytes / path / PIL.Image.Image, got "
            f"{type(source).__name__}"
        )


FileLike = Union[Path, str]
