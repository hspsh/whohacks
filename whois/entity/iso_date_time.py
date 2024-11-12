from dataclasses import dataclass
from datetime import datetime


@dataclass
class IsoDateTimeField:
    value: datetime

    @property
    def db_value(self) -> str:
        return self.value.isoformat()

    @property
    def python_value(self) -> datetime:
        return datetime.fromisoformat(self.value)
