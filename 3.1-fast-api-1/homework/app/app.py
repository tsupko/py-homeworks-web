# app/app.py

from typing import Annotated

from fastapi import FastAPI, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from dependencies import get_db_session
from lifespan import lifespan
from services import add_item, get_item, update_item, delete_item, search_items

app = FastAPI(
    title="Advertisements API",
    description="This is a REST API for buying and selling advertisements",
    version="0.0.1",
    lifespan=lifespan
)

# Создаём тип для зависимости сессии
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@app.post("/advertisement", response_model=schemas.CreateAdvertisementResponse, summary="Создать новое объявление")
async def create_advertisement(
        advertisement_data: schemas.CreateAdvertisementRequest,
        session: SessionDep
):
    new_advertisement = await add_item(session, models.Advertisement, advertisement_data)
    return schemas.CreateAdvertisementResponse(id=new_advertisement.id)


@app.get("/advertisement/{item_id}", response_model=schemas.GetAdvertisementResponse,
         summary="Получить объявление по ID")
async def get_advertisement(
        item_id: int,
        session: SessionDep
):
    advertisement = await get_item(session, models.Advertisement, item_id)
    return schemas.GetAdvertisementResponse(**advertisement.to_dict())


@app.patch("/advertisement/{item_id}", response_model=schemas.UpdateAdvertisementResponse,
           summary="Обновить объявление")
async def update_advertisement(
        item_id: int,
        update_data: schemas.UpdateAdvertisementRequest,
        session: SessionDep
):
    updated_advertisement = await update_item(session, models.Advertisement, item_id, update_data)
    return schemas.UpdateAdvertisementResponse(**updated_advertisement.to_dict())


@app.delete("/advertisement/{item_id}", response_model=schemas.OKResponse, summary="Удалить объявление")
async def delete_advertisement(
        item_id: int,
        session: SessionDep
):
    await delete_item(session, models.Advertisement, item_id)
    return schemas.OKResponse()


@app.get("/advertisement", response_model=list[schemas.GetAdvertisementResponse],
         summary="Поиск объявлений по фильтрам")
async def search_advertisements(
        session: SessionDep,
        title: str | None = Query(default=None, description="Заголовок объявления"),
        description: str | None = Query(default=None, description="Описание объявления"),
        author: str | None = Query(default=None, description="Автор объявления"),
        price: float | None = Query(default=None, description="Цена объявления")
):
    advertisements = await search_items(session, models.Advertisement, title=title, description=description,
                                        author=author, price=price)
    return [schemas.GetAdvertisementResponse(**adv.to_dict()) for adv in advertisements]
