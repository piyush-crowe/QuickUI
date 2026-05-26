from instantui.core.registry import Registry, app, registry


def test_app_decorator_registers_and_returns_fn():
    @app
    def hello(name: str = "world"):
        return f"hi {name}"

    assert len(registry) == 1
    assert registry[0].name == "hello"
    assert hello("a") == "hi a"


def test_registry_iter_and_doc_capture():
    @app
    def greet(name: str):
        """Say hi."""
        return name

    [entry] = list(registry)
    assert entry.doc == "Say hi."
    assert entry.fields[0].name == "name"


def test_fresh_registry_is_independent(fresh_registry: Registry):
    @fresh_registry.register
    def foo():
        return 1

    assert len(fresh_registry) == 1
    assert len(registry) == 0
