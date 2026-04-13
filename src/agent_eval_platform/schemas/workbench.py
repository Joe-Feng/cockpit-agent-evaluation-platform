from datetime import datetime
from typing import Any

from pydantic import BaseModel


class QuickActionRead(BaseModel):
    label: str
    href: str
    tone: str


class SummaryCardRead(BaseModel):
    id: str
    label: str
    value: str
    detail: str
    tone: str


class RunListItemRead(BaseModel):
    run_id: str
    status: str
    target_id: str
    env_id: str
    suite_ids: list[str]
    task_count: int
    passed_count: int
    created_at: datetime


class RunListRead(BaseModel):
    items: list[RunListItemRead]


class WorkbenchHomeRead(BaseModel):
    target_id: str
    summary_cards: list[SummaryCardRead]
    quick_actions: list[QuickActionRead]
    recent_runs: list[RunListItemRead]
    risk_items: list[dict[str, Any]]
