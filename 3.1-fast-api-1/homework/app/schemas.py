# app/schemas.py
from typing import Optional

from pydantic import BaseModel


class CreateAdvertisementRequest(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    author: str


class CreateAdvertisementResponse(BaseModel):
    id: int


class GetAdvertisementResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    price: float
    author: str
    created_at: Optional[str] = None


class UpdateAdvertisementRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    author: Optional[str] = None


class UpdateAdvertisementResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    price: float
    author: str
    created_at: Optional[str] = None


class OKResponse(BaseModel):
    status: str = "ok"
