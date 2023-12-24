from . import bindings


def exposed(_class):
    assert issubclass(_class, bindings.Node)
    return _class


def export(type, val):
    assert isinstance(val, type)
    return val
