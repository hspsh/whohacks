from datetime import datetime

import sqlalchemy.types as types


class IsoDateTimeField(types.TypeDecorator):
    impl = types.DATETIME

    def db_value(self, value: datetime) -> str:
        if value:
            return value.isoformat()

    def python_value(self, value: str) -> datetime:
        if value:
            return datetime.fromisoformat(value)