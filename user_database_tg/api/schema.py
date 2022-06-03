import re

from pydantic import BaseModel, validator, Field
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from user_database_tg.config import config
from user_database_tg.db.models import HackedUser

__all__ = [
    'HackedUserPydantic',
    'Item',
]
HackedUserPydantic = pydantic_model_creator(HackedUser)
HackedUserPydanticSet = pydantic_queryset_creator(HackedUser)

auth_tokens = []


class TransUser(BaseModel):
    user_id: int
    username: str | None
    locale: str | None
    duration: int
    token: str

    @validator("token")
    def correct(cls, v):
        if v != config.MAIN_API_TOKEN:
            raise ValueError('incorrect token')
        return v


class TokenUser(BaseModel):
    token: str
    user_token: str

    @validator("token")
    def correct(cls, v):
        if v != config.MAIN_API_TOKEN:
            raise ValueError('incorrect token')
        return v

    def delete(self):
        auth_tokens.remove(self.user_token)

    def add(self):
        auth_tokens.append(self.user_token)


class Authorization(BaseModel):
    token: str = Field(description="token for authentication")

    @validator("token")
    def correct(cls, v):
        if v not in auth_tokens:
            raise ValueError('incorrect token')
        return v


class Item(Authorization):
    email: str = Field(description="mail for database search")
    limit: int = Field(20, description="limit of returned objects")

    @validator("email")
    def correct(cls, v):
        match = re.match(r"[^@]+@[^@]+\.[^@]+", v.lower())
        if not match:
            raise ValueError('Incorrect email. Email example: test@mail.com')
        return v


class TestItem(BaseModel):
    token: str = "test_token"
    email: str = "blablas@icloud.com"
    limit: int = 5

    @validator("email")
    def correct(cls, v):
        match = re.match(r"[^@]+@[^@]+\.[^@]+", v.lower())
        if not match:
            raise ValueError('email incorrect')
        return v


class TestHackedUser(BaseModel):
    email: str
    password: str
    service: str
