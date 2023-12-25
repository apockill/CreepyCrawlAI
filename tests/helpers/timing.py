from time import time
from typing import Any


class Timer:
    def __init__(self) -> None:
        self.start: float | None = None
        self.end: float | None = None

    def __enter__(self) -> "Timer":
        self.start = time()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.end = time()

    @property
    def elapsed(self) -> float:
        assert self.start is not None
        if self.end is None:
            return time() - self.start
        return self.end - self.start
