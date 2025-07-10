from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fast_async.models import TodoState


class Message(BaseModel):
    message: str


class CreatedUser(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserID(CreatedUser):
    id: int


class ListUsers(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    token_access: str
    token_type: str


class FilterPage(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=0, default=10)


class FilterTodo(FilterPage):
    title: str | None = Field(default=None, min_length=3, max_length=22)
    description: str | None = None
    state: TodoState | None = None


class UpdateTodo(BaseModel):
    title: str | None
    description: str | None = None
    state: TodoState | None = None


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState = Field(default=TodoState.todo)


class TodoPublic(TodoSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class TodoList(BaseModel):
    todos: list[TodoPublic]
