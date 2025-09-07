from __future__ import annotations

from typing import Any, Callable, Tuple


def safe_call(fn: Callable[[], Any]) -> Tuple[bool, Any]:
    try:
        return True, fn()
    except Exception as e:
        return False, e


__all__ = ["safe_call"]
