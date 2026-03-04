from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


AuthType = Literal["bearer", "basic", "api_key"]


class ServiceBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    sub_prefix: str = Field(min_length=1, max_length=50)
    base_url: str = Field(min_length=1, max_length=500)
    auth_type: AuthType
    auth_value: str = Field(min_length=1)
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    sub_prefix: str | None = Field(default=None, min_length=1, max_length=50)
    base_url: str | None = Field(default=None, min_length=1, max_length=500)
    auth_type: AuthType | None = None
    auth_value: str | None = Field(default=None, min_length=1)
    is_active: bool | None = None


class ServiceOut(ServiceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UriMappingBase(BaseModel):
    path_pattern: str = Field(min_length=1, max_length=500)
    description: str | None = None
    is_active: bool = True


class UriMappingCreate(UriMappingBase):
    pass


class UriMappingOut(UriMappingBase):
    id: int
    service_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

