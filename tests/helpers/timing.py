from time import time


class Timer:
    def __init__(self):
        self.start, self.end = None, None

    def __enter__(self):
        self.start = time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time()

    @property
    def elapsed(self):
        if self.end is None:
            return time() - self.start
        return self.end - self.start
