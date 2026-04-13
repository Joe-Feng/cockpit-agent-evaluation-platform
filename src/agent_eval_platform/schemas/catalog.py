from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TargetCreate(BaseModel):
    id: str = Field(min_length=1)
    name: str
    adapter_types: list[str]
    profile: dict


class TargetRead(TargetCreate):
    pass


class EnvironmentCreate(BaseModel):
    id: str = Field(min_length=1)
    name: str
    profile: dict


class EnvironmentRead(EnvironmentCreate):
    pass


class AssetStatus(str, Enum):
    DRAFT = "draft"
    USED = "used"
    SUPERSEDED = "superseded"


class SuiteCreate(BaseModel):
    id: str = Field(min_length=1)
    mode: str
    definition: dict


class SuitePatch(BaseModel):
    definition: dict


class SuiteCopyRequest(BaseModel):
    id: str = Field(min_length=1)


class SuiteRead(BaseModel):
    id: str
    mode: str
    name: str
    definition: dict
    asset_status: AssetStatus
    version_group_id: str
    superseded_by_id: str | None
    case_count: int
    updated_at: datetime


class CaseCreate(BaseModel):
    id: str = Field(min_length=1)
    suite_id: str
    definition: dict


class CaseRead(CaseCreate):
    pass
