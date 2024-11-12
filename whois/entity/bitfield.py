from __future__ import annotations


class BitField:
    def __init__(self):
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

    def clear(self) -> None:
        """Set all bits of the BitMap to 0's"""
        self._flags = 0

    def __int__(self) -> int:
        return int(self._flags)

    def __repr__(self) -> str:
        return f"BitField({bin(self._flags)})"

    def __format__(self, format_spec):
        return self.__repr__()

    def __eq__(self, other: BitField) -> bool:
        return int(self) == int(other)

    def __hash__(self) -> int:
        return hash(self._flags)
