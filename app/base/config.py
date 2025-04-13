import os

from dotenv import load_dotenv

load_dotenv()


def get_postgres_url() -> str:
    """Получение URL подключения к базе данных PostgreSQL."""
    return (
        "postgresql+psycopg2://"
        + os.getenv("DB_USER")
        + ":"
        + os.getenv("DB_PASSWORD")
        + "@"
        + os.getenv("DB_HOST")
        + ":"
        + os.getenv("DB_PORT")
        + "/"
        + os.getenv("DB_NAME")
    )