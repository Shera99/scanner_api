"""Счётчики сеанса в памяти процесса.

Пересчёт по всему сеансу — самый тяжёлый запрос проверки билета. Между
пересчётами сервис отдаёт сохранённые числа и сам прибавляет к ним сканы,
прошедшие через этот процесс; сканы других процессов подтягиваются при
следующем пересчёте, не позже чем через ttl секунд.
"""
import time

from src.core.config import settings

_MAX_ENTRIES = 512

CountsKey = tuple[int, str]


class CountsCache:

    def __init__(self, ttl: float):
        self._ttl = ttl
        self._entries: dict[CountsKey, tuple[float, dict]] = {}

    def get(self, key: CountsKey, stale: bool = False) -> dict | None:
        entry = self._entries.get(key)
        if entry is None:
            return None
        expires_at, counts = entry
        if stale or expires_at > time.monotonic():
            return counts
        return None

    def put(self, key: CountsKey, counts: dict) -> None:
        if self._ttl <= 0:
            return
        if len(self._entries) >= _MAX_ENTRIES:
            now = time.monotonic()
            self._entries = {k: v for k, v in self._entries.items() if v[0] > now}
            if len(self._entries) >= _MAX_ENTRIES:
                self._entries.clear()
        self._entries[key] = (time.monotonic() + self._ttl, counts)

    def clear(self) -> None:
        self._entries.clear()


counts_cache = CountsCache(settings.counts_cache_ttl)
