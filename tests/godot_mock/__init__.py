from typing import Any

from . import bindings


def exposed(_class: Any) -> Any:
    assert issubclass(_class, bindings.Node)
    return _class


def export(type: Any, val: Any) -> Any:
    assert isinstance(val, type)
    return val
