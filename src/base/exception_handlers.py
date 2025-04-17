"""Модуль обработчиков исключений."""

from fastapi import HTTPException
from jwt import ExpiredSignatureError

from .exceptions import (
    AlreadyExistsException,
    DoesntExistException,
    InvalidTokenException,
    PermissionException,
    UnauthorizedException,
    InsufficientFundsException,
)


async def exception_handler_with_404_status(request, exc):
    """Обработчик исключений с кодом 404."""
    raise HTTPException(status_code=404, detail=str(exc))


async def exception_handler_with_400_status(request, exc):
    """Обработчик исключений с кодом 400."""
    raise HTTPException(status_code=400, detail=str(exc))


async def exception_handler_with_401_status(request, exc):
    """Обработчик исключений с кодом 401."""
    raise HTTPException(status_code=401, detail=str(exc))


async def exception_handler_with_403_status(request, exc):
    """Обработчик исключений с кодом 403."""
    raise HTTPException(status_code=403, detail=str(exc))


async def exception_handler_with_402_status(request, exc):
    """Обработчик исключений с кодом 402."""
    raise HTTPException(status_code=402, detail=str(exc))


EXCEPTION_HANDLERS = {
    DoesntExistException: exception_handler_with_404_status,
    AlreadyExistsException: exception_handler_with_400_status,
    InvalidTokenException: exception_handler_with_401_status,
    PermissionException: exception_handler_with_403_status,
    UnauthorizedException: exception_handler_with_401_status,
    ExpiredSignatureError: exception_handler_with_401_status,
    InsufficientFundsException: exception_handler_with_402_status,
}
