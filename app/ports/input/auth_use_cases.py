from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RegisterUserInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    full_name: str
    password: str


class RegisterUserOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    email: str
    full_name: str
    created_at: datetime


class LoginUserInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    password: str


class LoginUserOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str
    token_type: str = "bearer"


class IRegisterUser(ABC):
    @abstractmethod
    async def execute(self, data: RegisterUserInput) -> RegisterUserOutput: ...


class ILoginUser(ABC):
    @abstractmethod
    async def execute(self, data: LoginUserInput) -> LoginUserOutput: ...
