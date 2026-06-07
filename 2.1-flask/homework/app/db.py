import atexit
import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, Integer, String, DateTime, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, MappedColumn, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", 'app')
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", 'secret')
POSTGRES_HOST = os.getenv("POSTGRES_HOST", 'localhost')
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5431)
POSTGRES_DB = os.getenv("POSTGRES_DB", 'app')

DATABASE_URL = (f"postgresql+psycopg://"
                f"{POSTGRES_USER}:{POSTGRES_PASSWORD}"
                f"@{POSTGRES_HOST}:{POSTGRES_PORT}"
                f"/{POSTGRES_DB}")
# Создание движка SQLAlchemy для подключения к PostgreSQL
engine = create_engine(DATABASE_URL)
# Фабрика сессий для работы с базой данных
Session = sessionmaker(bind=engine)


# Тестовые пользователи для демонстрации работы API
# В реальном проекте пароли должны храниться в защищенной системе
test_users = {
    "user1@example.com": generate_password_hash("password123"),
    "user2@example.com": generate_password_hash("qwerty456"),
}


def verify_password(email: str, password: str) -> bool:
    """Проверяет корректность пароля для тестового пользователя.
    
    Args:
        email: Email пользователя
        password: Пароль для проверки
        
    Returns:
        True, если пароль верный, False в противном случае.
    """
    if email in test_users:
        return check_password_hash(test_users[email], password)
    return False


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy.
    
    Содержит общую структуру с полем id для всех таблиц.
    """
    id: MappedColumn[int] = mapped_column(Integer, primary_key=True)

    @property
    def dict(self):
        """Преобразует модель в словарь с идентификатором."""
        return {"id": self.id}


class User(Base):
    """Модель пользователя системы.
    
    Используется для аутентификации и авторизации.
    """
    __tablename__ = "users"
    email: MappedColumn[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: MappedColumn[str] = mapped_column(String, nullable=False)

    @property
    def dict(self):
        """Преобразует пользователя в словарь."""
        return {"id": self.id, "email": self.email}


class Ad(Base):
    """Модель объявления.
    
    Основная сущность API - объявление о продаже/покупке.
    """
    __tablename__ = "ads"
    title: MappedColumn[str] = mapped_column(String, unique=True)
    description: MappedColumn[str] = mapped_column(String)
    created: MappedColumn[datetime] = mapped_column(DateTime, server_default=func.now())
    owner: MappedColumn[str] = mapped_column(String)

    @property
    def dict(self):
        """Преобразует объявление в словарь для JSON-ответа."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created": self.created.isoformat(),
            "owner": self.owner
        }


# Создание всех таблиц в базе данных
Base.metadata.create_all(bind=engine)
# Закрытие соединения при завершении работы приложения
atexit.register(engine.dispose)
