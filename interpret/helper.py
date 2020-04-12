from sys import stderr, stdout
from typing import Callable


def exit_app(code: int, message: str = '', use_stderr: bool = False):
    print(message, file=stderr if use_stderr else stdout)
    exit(int(code.value))


def list_any(list: list, query: Callable[..., bool]):
    for item in list:
        if query(item):
            return True
    return False
