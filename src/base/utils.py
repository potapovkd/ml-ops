"""Утилиты."""

from datetime import datetime, timedelta, timezone
import pickle
from typing import Literal

import jwt
from langchain_community.retrievers import BM25Retriever

from base.data_structures import (
    AccessTokenDTO,
    JWTPayloadDTO,
    JWTPayloadExtendedDTO,
    TokenPairDTO,
)
from base.exceptions import InvalidTokenException


class JWTHandler:
    """
    Обработчик JWT.

    В качестве алгоритма используется симметричный HS256.
    """

    def __init__(
        self,
        secret_key: str,
        access_token_expire_minutes: int,
        refresh_token_expire_hours: int,
    ):
        """Инициализация класса."""
        self._secret_key = secret_key
        self._token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_hours = refresh_token_expire_hours

    def _create(
        self, payload: dict, token_type: Literal["refresh", "access"]
    ) -> bytes:
        """Создание токена."""
        match token_type:
            case "access":
                expired_time = timedelta(minutes=self._token_expire_minutes)
            case "refresh":
                expired_time = timedelta(
                    hours=self._refresh_token_expire_hours
                )
            case _:
                raise ValueError("Некорректный аргумент token_type")
        return jwt.encode(
            {
                **payload,
                "token_type": token_type,
                "exp": datetime.now(tz=timezone.utc) + expired_time,
            },
            key=self._secret_key,
        )

    def _get_payload_from_token(self, token: str) -> JWTPayloadExtendedDTO:
        try:
            return JWTPayloadExtendedDTO(
                **jwt.decode(
                    jwt=token,
                    key=self._secret_key,
                    algorithms=["HS256"],
                )
            )
        except jwt.ExpiredSignatureError:
            raise InvalidTokenException("Срок действия токена истек.")
        except jwt.DecodeError:
            raise InvalidTokenException("Некорректный токен")

    def create_token_pair(self, payload: JWTPayloadDTO) -> TokenPairDTO:
        """Создание пары access и refresh токенов."""
        return TokenPairDTO(
            access_token=self._create(payload.model_dump(), "access"),
            refresh_token=self._create(payload.model_dump(), "refresh"),
        )

    def create_new_access_token_by_refresh_token(
        self, token: str
    ) -> AccessTokenDTO:
        """Создание нового access токена по refresh токену."""
        payload = self._get_payload_from_token(token)
        if payload.token_type != "refresh":
            raise InvalidTokenException("Некорректный refresh токен")
        return AccessTokenDTO(
            access_token=self._create(payload.model_dump(), "access")
        )

    def get_data_from_access_token(self, token: str) -> JWTPayloadDTO:
        """Получение данных из access токена."""
        payload = self._get_payload_from_token(token)
        if payload.token_type != "access":
            raise InvalidTokenException("Некорректный access токен")
        return JWTPayloadDTO(**payload.model_dump())


def load_retriever(load_path: str) -> BM25Retriever:
    """Загружает ретривер из pkl."""
    with open(load_path, "rb") as f:
        return pickle.load(f)
