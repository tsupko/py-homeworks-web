# app/services.py
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

import models


async def add_item(
        session: AsyncSession,
        orm_model: type,
        item_data: BaseModel
) -> models.Advertisement:
    """
    Универсальная функция для добавления записи в БД.
    """
    new_item = orm_model(**item_data.model_dump())
    session.add(new_item)
    try:
        await session.commit()
        await session.refresh(new_item)
        return new_item
    except Exception:
        await session.rollback()
        raise


async def get_item(
        session: AsyncSession,
        orm_model: type,
        item_id: int
) -> models.Advertisement:
    """
    Получает запись по ID или выбрасывает 404.
    """
    stmt = select(orm_model).where(orm_model.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{orm_model.__name__} with id {item_id} not found"
        )
    return item


async def update_item(
        session: AsyncSession,
        orm_model: type,
        item_id: int,
        update_data: BaseModel
) -> models.Advertisement:
    """
    Обновляет запись.
    """
    item = await get_item(session, orm_model, item_id)

    # Преобразуем update_data в словарь, исключая поля со значением None
    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(item, key, value)

    await session.commit()
    await session.refresh(item)
    return item


async def delete_item(
        session: AsyncSession,
        orm_model: type,
        item_id: int
) -> None:
    """
    Удаляет запись.
    """
    item = await get_item(session, orm_model, item_id)
    await session.delete(item)
    await session.commit()


async def search_items(
        session: AsyncSession,
        orm_model: type,
        **filters
) -> list[models.Advertisement]:
    """
    Ищет записи по переданным фильтрам (логическое И).
    """
    conditions = []
    for key, value in filters.items():
        if value is not None:
            conditions.append(getattr(orm_model, key) == value)

    if conditions:
        stmt = select(orm_model).where(and_(*conditions))
    else:
        stmt = select(orm_model)

    result = await session.execute(stmt)
    items = result.scalars().all()
    return items
