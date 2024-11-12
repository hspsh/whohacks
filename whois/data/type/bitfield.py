import sqlalchemy.types as types
from sqlalchemy.ext.mutable import Mutable

from whois.entity.bitfield import BitField


class BitField(BitField, types.TypeDecorator, Mutable):
    impl = types.Integer()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        """Convert BitField to integer before storing in the database."""
        if isinstance(value, BitField):
            return int(value)
        elif isinstance(value, int):
            return value
        return 0  # Default to 0 if None or invalid type

    def process_result_value(self, value, dialect):
        """Convert integer from database back into a BitField instance."""
        bitfield = BitField()
        if value is not None:
            bitfield._flags = value  # directly set flags based on stored integer
        return bitfield
