import datetime
import os

from sqlalchemy import DateTime, Integer, String, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")
POSTGRES_USER = os.getenv("POSTGRES_USER", "app")
POSTGRES_DB = os.getenv("POSTGRES_DB", "app")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")

POSTGRES_DSN = (
    f"postgresql+asyncpg://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

engine = create_async_engine(POSTGRES_DSN, echo=True)
Session = async_sessionmaker(engine, expire_on_commit=False)


async def verify_password(session: AsyncSession, email: str, password: str) -> str | None:
    """Проверяет пароль и возвращает email пользователя или None."""
    from db import User
    result = await session.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    if user and check_password_hash(user.password_hash, password):
        return email
    return None


async def register_user(session: AsyncSession, email: str, password: str):
    """Регистрирует нового пользователя или вызывает 409, если пользователь уже существует."""
    from db import User
    user = User(email=email, password_hash=generate_password_hash(password))
    session.add(user)
    try:
        await session.commit()
        return user
    except IntegrityError:
        raise IntegrityError("Пользователь уже существует", None, None)


class Base(DeclarativeBase, AsyncAttrs):
    id: MappedColumn[int] = mapped_column(Integer, primary_key=True)

    @property
    def id_dict(self):
        return {"id": self.id}


class User(Base):
    __tablename__ = "users"
    email: MappedColumn[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: MappedColumn[str] = mapped_column(String, nullable=False)

    @property
    def json(self):
        return {"id": self.id, "email": self.email}


class Ad(Base):
    __tablename__ = "ads"
    title: MappedColumn[str] = mapped_column(String, unique=True)
    description: MappedColumn[str] = mapped_column(String)
    created: MappedColumn[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    owner: MappedColumn[str] = mapped_column(String)

    @property
    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created": self.created.isoformat(),
            "owner": self.owner
        }


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()
