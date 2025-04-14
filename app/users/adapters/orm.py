"""Модуль реализации ORM."""

from datetime import datetime
from typing import Annotated

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from base.orm import Base

created_at = Annotated[datetime, mapped_column(server_default=func.now())]


class UserORM(Base):
    """Модель пользователей."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    created_at: Mapped[created_at]

    chats: Mapped[list["ChatORM"]] = relationship(back_populates="user")
    account: Mapped["AccountORM"] = relationship(back_populates="user", uselist=False)


class AccountORM(Base):
    """Модель личного счета."""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    user: Mapped[UserORM] = relationship(back_populates="account")
    transactions: Mapped[list["TransactionORM"]] = relationship(back_populates="account")


class TransactionORM(Base):
    """Модель транзакции."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    amount: Mapped[float]
    transaction_type: Mapped[int]
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)

    account: Mapped[AccountORM] = relationship(back_populates="transactions")
