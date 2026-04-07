from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class AdapterResult:
    status_code: int
    body: Any | None
    raw_text: str


class TargetAdapter(Protocol):
    def execute(self, **kwargs) -> AdapterResult:
        ...
