from typing import TypeVar

IntOrFloat = TypeVar("IntOrFloat", int, float)


def clamp(val: IntOrFloat, lower: IntOrFloat, upper: IntOrFloat) -> IntOrFloat:
    """Performant clamp function"""
    return lower if val < lower else upper if val > upper else val
