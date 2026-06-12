# app/schemas.py
from typing import Optional

from pydantic import BaseModel


class CreateTodoRequest(BaseModel):
    title: str
    important: bool = False


class CreateTodoResponse(BaseModel):
    id: int


class GetTodoResponse(BaseModel):
    id: int
    title: str
    important: bool
    done: bool
    start_time: Optional[str] = None
    finish_time: Optional[str] = None


class UpdateTodoRequest(BaseModel):
    title: Optional[str] = None
    important: Optional[bool] = None
    done: Optional[bool] = None


class UpdateTodoResponse(BaseModel):
    id: int
    title: str
    important: bool
    done: bool
    start_time: Optional[str] = None
    finish_time: Optional[str] = None


class OKResponse(BaseModel):
    status: str = "ok"
