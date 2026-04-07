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


class SuiteCreate(BaseModel):
    id: str = Field(min_length=1)
    mode: str
    definition: dict


class SuiteRead(SuiteCreate):
    pass


class CaseCreate(BaseModel):
    id: str = Field(min_length=1)
    suite_id: str
    definition: dict


class CaseRead(CaseCreate):
    pass
