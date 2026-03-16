from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class IBaseRepository(ABC, Generic[T]):

    @abstractmethod
    async def get_by_id(self, id: int) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, entity: T) -> T:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: T) -> T:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entity: T) -> None:
        raise NotImplementedError

    @abstractmethod
    async def save(self, entity: T) -> T:
        raise NotImplementedError
