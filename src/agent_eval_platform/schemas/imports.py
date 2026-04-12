from typing import Literal

from pydantic import BaseModel


class BenchmarkPackageTargetBinding(BaseModel):
    target_id: str
    adapter_type: str
    mode: str


class BenchmarkPackageSuite(BaseModel):
    id: str
    name: str
    mode: str
    description: str
    case_count: int
    source_summary: dict


class BenchmarkPackageCase(BaseModel):
    id: str
    source_test_case_id: str
    definition: dict


class BenchmarkAgentPackage(BaseModel):
    schema_version: Literal["benchmark-agent-export/v1"]
    export_id: str
    export_profile: str
    target_binding: BenchmarkPackageTargetBinding
    source: dict
    filters: dict
    suite: BenchmarkPackageSuite
    cases: list[BenchmarkPackageCase]


class BenchmarkPackageImportRequest(BaseModel):
    env_id: str
    package: BenchmarkAgentPackage


class BenchmarkPackageImportSummary(BaseModel):
    target_id: str
    env_id: str
    suite_id: str
    case_count: int
