from __future__ import annotations

from collections import OrderedDict
from typing import Any


class InMemoryCache:
    def __init__(self, max_size: int = 10_000) -> None:
        self.max_size = max_size
        self._items: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> dict[str, Any] | None:
        value = self._items.get(key)
        if value is None:
            self.misses += 1
            return None
        self.hits += 1
        self._items.move_to_end(key)
        return value

    def set(self, key: str, value: dict[str, Any]) -> None:
        self._items[key] = value
        self._items.move_to_end(key)
        if len(self._items) > self.max_size:
            self._items.popitem(last=False)

    @property
    def size(self) -> int:
        return len(self._items)
