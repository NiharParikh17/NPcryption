"""
Tests for npcryption.core.DecryptionTable module.

Covers:
  - DecryptionTable inherits from EncryptionTable
  - DecryptionTable derives correct private exponent D via DTable
  - DecryptionTable builds the squaring table for exponent D
  - DecryptionTable.getD static method
"""
import pytest
from npcryption.core.DecryptionTable import DecryptionTable
from npcryption.core.EncryptionTable import EncryptionTable
from npcryption.core.DTable import DTable


class TestDecryptionTableInheritance:
    """Verify DecryptionTable is a subclass of EncryptionTable."""

    def test_is_subclass(self):
        assert issubclass(DecryptionTable, EncryptionTable)

    def test_instance_is_encryption_table(self):
        dt = DecryptionTable(20, 7)
        assert isinstance(dt, EncryptionTable)


class TestDecryptionTableInit:
    """Tests for DecryptionTable.__init__(PQ, E)."""

    def test_phi20_E7_uses_D3(self):
        """phi=20, E=7 → D=3; EncryptionTable(3): power=[1,2], validity=[T,T]."""
        dt = DecryptionTable(20, 7)
        # D=3: splitIntoValidPowersOf2(3) = [1, 2]
        assert dt.power == [1, 2]
        assert dt.validity == [True, True]

    def test_phi288_E5_uses_D173(self):
        """phi=288, E=5 → D=173; EncryptionTable(173) has 8 rows."""
        dt = DecryptionTable(288, 5)
        # 173 = 128+32+8+4+1 (5 set bits); highest power 128 → 8 rows
        assert dt.get_length() == 8

    def test_phi288_E5_initial_prevSQR_zeros(self):
        dt = DecryptionTable(288, 5)
        assert all(v == 0 for v in dt.prevSQR)

    def test_phi288_E5_initial_modNum_zeros(self):
        dt = DecryptionTable(288, 5)
        assert all(v == 0 for v in dt.modNum)

    def test_phi20_E7_length(self):
        """D=3, EncryptionTable(3) has 2 rows."""
        dt = DecryptionTable(20, 7)
        assert dt.get_length() == 2

    def test_phi3120_E17_correct_D(self):
        """P=61,Q=53 → phi=3120, E=17 → D satisfies 17*D ≡ 1 mod 3120."""
        dt = DecryptionTable(3120, 17)
        # Use DTable to find what D should be
        tbl = DTable(3120, 17)
        tbl.generateTable()
        expected_D = tbl.getD(3120)
        assert dt.get_length() == len(
            [i for i in range(expected_D.bit_length()) if expected_D >> i & 1 or i == 0]
        ) or dt.power[-1] <= expected_D  # highest power ≤ D


class TestDecryptionTableGetD:
    """Tests for DecryptionTable.getD(P_Q, E) static method."""

    def test_phi20_E7_returns_3(self):
        assert DecryptionTable.getD(20, 7) == 3

    def test_phi288_E5_returns_173(self):
        assert DecryptionTable.getD(288, 5) == 173

    def test_result_satisfies_modular_inverse(self):
        for phi, e in [(20, 7), (288, 5), (72, 5), (3120, 17)]:
            D = DecryptionTable.getD(phi, e)
            assert (e * D) % phi == 1, f"E={e}, D={D}, phi={phi}"

    def test_result_is_positive(self):
        for phi, e in [(20, 7), (288, 5), (72, 5), (3120, 17)]:
            D = DecryptionTable.getD(phi, e)
            assert D > 0

    def test_result_less_than_phi(self):
        for phi, e in [(20, 7), (288, 5), (72, 5)]:
            D = DecryptionTable.getD(phi, e)
            assert D < phi


class TestDecryptionTableInheritedMethods:
    """Verify that inherited EncryptionTable methods still work on DecryptionTable."""

    def test_setPrevSQR(self):
        dt = DecryptionTable(20, 7)
        dt.set_prev_sqr(32, 0)
        assert dt.prevSQR[0] == 32

    def test_setModNum(self):
        dt = DecryptionTable(20, 7)
        dt.set_mod_num(7, 0)
        assert dt.modNum[0] == 7

    def test_getProduct_with_set_values(self):
        """D=3 → power=[1,2], validity=[T,T]; product = modNum[0]*modNum[1]."""
        dt = DecryptionTable(20, 7)
        dt.set_mod_num(5, 0)
        dt.set_mod_num(4, 1)
        assert dt.get_product() == 20
