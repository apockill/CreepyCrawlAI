from typing import Generator


class Position:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"Position(x={self.x}, y={self.y})"

    def __iter__(self) -> Generator[int, None, None]:
        yield self.x
        yield self.y

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        raise ValueError(f"Cannot compare Position to {type(other)}")

    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)

    def __mul__(self, other: int) -> "Position":
        return Position(self.x * other, self.y * other)
