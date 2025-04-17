from enum import Enum
import os

from dotenv import load_dotenv

load_dotenv()


def get_postgres_url() -> str:
    """Получение URL подключения к базе данных PostgreSQL."""
    return (
        "postgresql+asyncpg://"
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


def show_sql_logs() -> bool:
    """Показывать ли логи SQL-запросов."""
    return os.getenv("SHOW_SQL_LOGS") == "True"


def get_secret_key() -> str:
    """Получение секретного ключа."""
    return os.getenv("SECRET_KEY")


def get_allowed_hosts() -> list[str]:
    """Получение допустимых хостов."""
    if not os.getenv("ALLOWED_HOSTS"):
        return ["*"]
    return os.getenv("ALLOWED_HOSTS", "").split(",")


def get_api_prefix() -> str:
    """Получение префикса API."""
    return os.getenv("API_PREFIX") or "/api/v1/"


def get_access_token_expires_minutes() -> int:
    """Получение времени жизни access токена в минутах."""
    if os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES"):
        return int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES"))
    return 60


def get_refresh_token_expires_hours() -> int:
    """Получение времени жизни refresh токена в часах."""
    if os.getenv("REFRESH_TOKEN_EXPIRES_HOURS"):
        return int(os.getenv("REFRESH_TOKEN_EXPIRES_HOURS"))
    return 24


def get_time_for_getting_jwt_from_ws() -> int:
    """Получение времени для предоставления JWT через WebSocket."""
    if os.getenv("TIME_FOR_GETTING_JWT_FROM_WS"):
        return int(os.getenv("TIME_FOR_GETTING_JWT_FROM_WS"))
    return 5


def get_llm_url() -> str:
    """Получение пути до микросервиса большой языковой модели."""
    return f"http://{os.getenv('LLM_HOST')}:{os.getenv('LLM_PORT')}"


def get_max_tokens_for_model() -> int:
    """Получение размера контекстного окна модели."""
    if os.getenv("N_TOKENS"):
        return int(os.getenv("N_TOKENS"))
    return 5_000


def get_n_relevant_docs_for_faiss() -> int:
    """Получение размера топа релевантных документов для извлечения."""
    if os.getenv("N_DOCS"):
        return int(os.getenv("N_DOCS"))
    return 5


def get_embedding_model_path() -> str:
    """Получение пути до модели эмбеддингов."""
    return (
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        + "/"
        + os.getenv("EMBEDDING_MODEL_PATH")
    )


def get_faiss_store_path() -> str:
    """Получение пути до векторной БД."""
    return (
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        + "/"
        + os.getenv("FAISS_PATH")
    )


def get_bm25_retriever_path() -> str:
    """Получение пути BM25 ретривера."""
    return (
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        + "/"
        + os.getenv("BM25_RETRIEVER_PATH")
    )


class ChatTypeChoice(Enum):
    """Типы чатов."""

    WITH_LLM = "with_llm"
    ONLY_RAG = "only_rag"


class RagTypeChoice(Enum):
    """Типы RAG-систем."""

    FAISS = "faiss"
    BM25 = "bm25"
