"""Модуль реализации паттерна репозиторий."""

import abc

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from base.entities import TransactionType
from base.exceptions import AlreadyExistsException, DoesntExistException
from .orm import UserORM, TransactionORM
from ..domain.models import User, UserCredentials, TransactionData

ALREADY_EXISTS_EXC_MESSAGE = "Создаваемый пользователь уже существует."
DOESNT_EXISTS_EXC_MESSAGE = "Пользователь не найден."


class UserAbstractDatabaseRepository(abc.ABC):
    """Абстрактный репозиторий базы данных."""

    @abc.abstractmethod
    async def get(self, user_id: int) -> User:
        """Получение объекта-пользователя из БД."""

    @abc.abstractmethod
    async def add(self, credentials: UserCredentials) -> None:
        """Добавление объекта-пользователя в БД."""

    @abc.abstractmethod
    async def delete(self, user_id: int) -> None:
        """Удаление объекта-пользователя из БД."""

    @abc.abstractmethod
    async def get_users(self) -> list[User]:
        """Получение списка всех объектов-пользователей из БД."""

    @abc.abstractmethod
    async def login(self, credentials: UserCredentials) -> User:
        """Проверка учетных данных пользователя."""

    @abc.abstractmethod
    async def get_user_balance(self, user_id: int) -> float:
        """Получение баланса личного счета."""

    async def add_transaction(
        self, user_id: int, data: TransactionData
    ) -> None:
        """Добавление транзакции для пользователя."""

    async def get_transactions(self, user_id: int) -> list[TransactionData]:
        """Получение истории транзакций."""


class UserSQLAlchemyRepository(UserAbstractDatabaseRepository):
    """Репозиторий базы данных SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        """Инициализация репозитория."""
        self.session = session

    async def _get(self, raise_exc: bool = True, **filters) -> UserORM | None:
        """
        Получение объекта-пользователя из БД.

        С возможностью выброса исключения.
        """
        user = await self.session.execute(select(UserORM).filter_by(**filters))
        user = user.scalars().one_or_none()
        if not user and raise_exc:
            raise DoesntExistException(DOESNT_EXISTS_EXC_MESSAGE)
        return user

    async def get(self, user_id: int) -> User:
        """Получение объекта-пользователя из БД."""
        user = await self._get(user_id=user_id)
        return User(**user.__dict__)

    async def add(self, credentials: UserCredentials) -> None:
        """Добавление объекта-пользователя в БД."""
        existed_user = await self._get(
            raise_exc=False, email=credentials.email
        )
        if existed_user:
            raise AlreadyExistsException(ALREADY_EXISTS_EXC_MESSAGE)
        user = UserORM(
            email=credentials.email,
            password=credentials.password,
        )
        self.session.add(user)

    async def delete(self, user_id: int) -> None:
        """Удаление объекта-пользователя из БД."""
        user = await self._get(user_id=user_id)
        await self.session.delete(user)

    async def get_users(self) -> list[User]:
        """Получение списка всех объектов-пользователей из БД."""
        users = await self.session.execute(select(UserORM))
        return [User(**user.__dict__) for user in users.scalars().all()]

    async def login(self, credentials: UserCredentials) -> User:
        """Проверка учетных данных пользователя."""
        user = await self._get(
            email=credentials.email,
            password=credentials.password,
        )
        return User(**user.__dict__)

    async def get_user_balance(self, user_id: int) -> float:
        """Получение баланса личного счета."""
        income_query = select(func.sum(TransactionORM.amount)).where(
            TransactionORM.user_id == user_id,
            TransactionORM.transaction_type == TransactionType.INCOME,
        )
        result_income = await self.session.execute(income_query)
        income_sum = result_income.scalar() or 0

        expense_query = select(func.sum(TransactionORM.amount)).where(
            TransactionORM.user_id == user_id,
            TransactionORM.transaction_type == TransactionType.EXPENSE,
        )
        result_expense = await self.session.execute(expense_query)
        expense_sum = result_expense.scalar() or 0

        return income_sum - expense_sum

    async def add_transaction(
        self, user_id: int, data: TransactionData
    ) -> None:
        """Добавление транзакции для пользователя."""
        transaction = TransactionORM(**data.model_dump(), user_id=user_id)
        self.session.add(transaction)

    async def get_transactions(self, user_id: int) -> list[TransactionData]:
        """Получение истории транзакций."""
        transactions = await self.session.execute(select(TransactionORM).filter_by(user_id=user_id))
        return [TransactionData(**transaction.__dict__) for transaction in transactions.scalars().all()]
