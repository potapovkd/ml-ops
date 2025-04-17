"""Бизнес-логика."""

import hashlib

from base.exceptions import DoesntExistException, UnauthorizedException
from ..domain.models import User, UserCredentials, TransactionData
from ..services.unit_of_work import UserAbstractUnitOfWork


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(self, uow: UserAbstractUnitOfWork, secret_key: str):
        """Инициализация сервиса."""
        self._uow = uow
        self._secret_key = secret_key

    def _hash_password(self, password: str) -> str:
        """Хеширование пароля."""
        return hashlib.sha512(
            (password + self._secret_key).encode()
        ).hexdigest()

    async def get_user(self, user_id: int) -> User:
        """Получение пользователя."""
        async with self._uow as uow:
            return await uow.users.get(user_id)

    async def delete_user(self, user_id: int) -> None:
        """Удаление пользователя."""
        async with self._uow as uow:
            await uow.users.delete(user_id)
            await uow.commit()

    async def add_user(self, user: UserCredentials) -> None:
        """Добавление пользователя."""
        user.password = self._hash_password(user.password)
        async with self._uow as uow:
            await uow.users.add(user)
            await uow.commit()

    async def login_user(self, credentials: UserCredentials) -> User:
        """Аутентификация пользователя."""
        credentials.password = self._hash_password(credentials.password)
        async with self._uow as uow:
            try:
                return await uow.users.login(credentials)
            except DoesntExistException:
                raise UnauthorizedException(
                    "Пользователя с таким учетными данными не существует."
                )

    async def get_user_balance(self, user_id: int) -> float:
        """Получение баланса пользователя."""
        async with self._uow as uow:
            return await uow.users.get_user_balance(user_id)

    async def add_transaction_for_user(
        self, user_id: int, data: TransactionData
    ) -> None:
        """Добавление транзакции."""
        async with self._uow as uow:
            await uow.users.add_transaction(user_id, data)
            await uow.commit()

    async def get_transactions_for_user(self, user_id: int) -> list[TransactionData]:
        async with self._uow as uow:
            return await uow.users.get_transactions(user_id)
