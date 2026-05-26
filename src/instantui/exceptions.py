"""Exception types raised by InstantUI."""


class InstantUIError(Exception):
    """Base class for all InstantUI errors."""


class NoFunctionsRegisteredError(InstantUIError):
    """Raised when ``run()`` is called with no registered functions."""


class FieldCastError(InstantUIError):
    """Raised when an incoming form value cannot be cast to the declared type."""
