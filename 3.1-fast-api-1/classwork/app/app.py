# app/app.py

from typing import Annotated

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from dependencies import get_db_session
from lifespan import lifespan
from services import add_item, get_item, update_item, delete_item

app = FastAPI(
    title="My ToDo App",
    description="This is a very simple todo application API",
    version="0.0.1",
    lifespan=lifespan
)

# Создаём тип для зависимости сессии
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@app.post("/v1/todo", response_model=schemas.CreateTodoResponse, summary="Создать новую задачу")
async def create_todo(
        todo_data: schemas.CreateTodoRequest,
        session: SessionDep
):
    # Используем сервисную функцию
    new_todo = await add_item(session, models.Todo, todo_data)
    return schemas.CreateTodoResponse(id=new_todo.id)


@app.get("/v1/todo/{item_id}", response_model=schemas.GetTodoResponse, summary="Получить задачу по ID")
async def get_todo(
        item_id: int,
        session: SessionDep
):
    todo = await get_item(session, models.Todo, item_id)
    # Преобразуем ORM-модель в словарь и затем в Pydantic-схему
    return schemas.GetTodoResponse(**todo.to_dict())


@app.patch("/v1/todo/{item_id}", response_model=schemas.UpdateTodoResponse, summary="Обновить задачу")
async def update_todo(
        item_id: int,
        update_data: schemas.UpdateTodoRequest,
        session: SessionDep
):
    updated_todo = await update_item(session, models.Todo, item_id, update_data)
    return schemas.UpdateTodoResponse(**updated_todo.to_dict())


@app.delete("/v1/todo/{item_id}", response_model=schemas.OKResponse, summary="Удалить задачу")
async def delete_todo(
        item_id: int,
        session: SessionDep
):
    await delete_item(session, models.Todo, item_id)
    return schemas.OKResponse()
