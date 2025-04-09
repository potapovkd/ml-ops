from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr

class UserCredentials(BaseModel):
    """Модель учетных данных пользователя."""

    email: EmailStr
    password: str


class UserMetadata(BaseModel):
    """Модель метаданных пользователя."""

    id: int
    created_at: datetime


class User(UserCredentials, UserMetadata):
    """Модель пользователя."""


class AccountBalance(BaseModel):
    """Модель данных личного счета пользователя."""

    id: int
    user_id: int


class Transaction(BaseModel):
    """Модель данных транзакции."""

    id: int
    account_id: int
    amount: float
    transaction_type: Literal["income", "expense"]