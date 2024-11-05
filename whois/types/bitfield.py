from __future__ import annotations

import sqlalchemy.types as types
from sqlalchemy.ext.mutable import Mutable


class BitField(Mutable, types.TypeDecorator):
    impl = types.INTEGER

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flags = 0

    def has_flag(self, mask: int) -> bool:
        """Check if specific flag is set"""
        return (self._flags & mask) == mask

    def set_flag(self, mask: int) -> None:
        """Set the specifig flag in the bitfield. Can set many bits at once."""
        self._flags |= mask

    def unset_flag(self, mask: int) -> None:
        """Un-set the specifig flag in the bitfield. Can un-set many bits at once"""
        self._flags &= ~mask

    def __int__(self) -> int:
        return int(self._flags)

    def __repr__(self) -> str:
        return f"BitField({bin(self._flags)})"

    def __eq__(self, other: BitField) -> bool:
        return int(self) == int(other)
