from dataclasses import dataclass
from datetime import datetime


@dataclass
class IsoDateTimeField:
    value: datetime

    @property
    def db_value(self) -> str:
        return self.value.isoformat()

    # def python_value(self, value: str) -> datetime:
    #     if value:
    #         return datetime.fromisoformat(value)
