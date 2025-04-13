"""Модуль реализации ORM."""

from typing import Annotated

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase

str_255 = Annotated[str, 255]


class Base(DeclarativeBase):
    """Базовый класс ORM."""

    type_annotation_map = {
        str_255: String(255),
    }

    def __repr__(self):
        """Представление объекта."""
        return f"<{self.__class__.__name__} {self.__dict__}>"

    def to_dict_with_property(self):
        """Сериализация ORM объекта с учетом property."""
        serialized_data = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

        properties = {
            attr: getattr(self, attr)
            for attr in dir(self.__class__)
            if isinstance(getattr(self.__class__, attr), property)
        }

        serialized_data.update(properties)
        return serialized_data
