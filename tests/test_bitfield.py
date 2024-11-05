from unittest import TestCase

from whois.types.bitfield import BitField


class BitFieldTest(TestCase):

    def test_setup(self):
        """The BitField can be initialized"""
        bf = BitField()
        assert bf

    def test_initial_state(self):
        """The BitFields initial state is 0"""
        bf = BitField()
        assert int(bf) == 0

    def test_set_flag(self):
        """The BitFields single flag can be set"""
        bf = BitField()
        bf.set_flag(1)
        assert bf.has_flag(1)

    def test_set_flags(self):
        """The BitFields many flags can be set"""
        bf1 = BitField()
        bf1.set_flag(1)
        bf1.set_flag(4)

        bf2 = BitField()
        bf2.set_flag(5)

        assert int(bf1) == int(0b101)
        assert bf1 == bf2

    def test_unset_flag(self):
        """The BitFields single flag can be unset"""
        bf = BitField()
        bf.set_flag(5)
        assert bf.has_flag(5)

        bf.unset_flag(5)
        assert int(bf) == 0

    def test_unset_flag_part(self):
        """The BitField flags part can be unset"""
        bf = BitField()
        bf.set_flag(7)
        assert bf.has_flag(7)

        bf.unset_flag(4)
        assert int(bf) == 3
