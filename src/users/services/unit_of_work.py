"""Реализация паттерна Unit of Work."""

import abc

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
)

from ..adapters.repositories import (
    UserAbstractDatabaseRepository,
    UserSQLAlchemyRepository,
)


class UserAbstractUnitOfWork(abc.ABC):
    """Абстракция над атомарной операцией (единицей работы)."""

    @property
    @abc.abstractmethod
    def users(self) -> UserAbstractDatabaseRepository:
        """Репозиторий для работы с чатами."""

    async def __aenter__(self) -> "UserAbstractUnitOfWork":
        """Инициализация UoW через менеджер контекста."""
        return self

    async def __aexit__(self, *args):
        """Откат транзакции из-за исключения."""
        await self.rollback()

    @abc.abstractmethod
    async def commit(self):
        """Фиксация транзакции."""

    @abc.abstractmethod
    async def rollback(self):
        """Откат транзакции."""


class UserSqlAlchemyUnitOfWork(UserAbstractUnitOfWork):
    """UoW для SQLAlchemy."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """Инициализация UoW."""
        self._session_factory = session_factory

    async def __aenter__(self):
        """Инициализация UoW через менеджер контекста."""
        self.session = self._session_factory()
        self._users = UserSQLAlchemyRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        """Откат транзакции из-за исключения."""
        await super().__aexit__(*args)
        await self.session.close()

    @property
    def users(self) -> UserSQLAlchemyRepository:
        """Репозиторий SQLAlchemy для работы с чатами."""
        return self._users

    async def commit(self):
        """Фиксация транзакции."""
        await self.session.commit()

    async def rollback(self):
        """Откат транзакции."""
        await self.session.rollback()
