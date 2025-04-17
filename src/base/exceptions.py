"""Модуль общих исключений предметной области."""


class DoesntExistException(Exception):
    """Исключение при попытке получения несуществующего объекта."""


class AlreadyExistsException(Exception):
    """Исключение при попытке создать уже существующий объект."""


class InvalidTokenException(Exception):
    """Исключение при невалидном токене."""


class PermissionException(Exception):
    """Исключение при попытке получения объекта без прав доступа."""


class UnauthorizedException(Exception):
    """Исключение при ошибке авторизации."""


class EmptyMessageException(Exception):
    """Исключение при получении пустого сообщения."""


class InsufficientFundsException(Exception):
    """Исключение при недостатке средств."""
