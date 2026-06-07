from pydantic import BaseModel, ValidationError, field_validator

from errors import HttpError


class BaseUser(BaseModel):
    name: str
    password: str

    @field_validator("password")
    @classmethod
    def secure_password(cls, v):
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters long")
        return v


class CreateUser(BaseUser):
    pass


class UpdateUser(BaseUser):
    name: str | None = None
    password: str | None = None


def validate(schema_cls: type[CreateUser, UpdateUser], data: dict) -> dict:
    try:
        schema = schema_cls(**data)
        return schema.model_dump(exclude_unset=True)
    except ValidationError as error:
        raise HttpError(400, "Bad requers")
