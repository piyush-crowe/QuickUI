import pytest

from instantui.core.registry import Registry, registry


@pytest.fixture(autouse=True)
def _reset_registry():
    """Isolate the module-level registry between tests."""
    registry.clear()
    yield
    registry.clear()


@pytest.fixture
def fresh_registry() -> Registry:
    return Registry()
