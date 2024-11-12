from datetime import datetime

import sqlalchemy.types as types


class IsoDateTimeField(types.TypeDecorator):
    impl = types.DATETIME
