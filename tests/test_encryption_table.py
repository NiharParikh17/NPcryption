"""
Tests for npcryption.core.EncryptionTable module.

Covers:
  - splitIntoValidPowersOf2()
  - getHighestPowerOf2()
  - EncryptionTable class: __init__, initialize, setPrevSQR, setModNum,
    getProduct, getLength
"""
import pytest
from npcryption.core.EncryptionTable import (
    splitIntoValidPowersOf2,
    getHighestPowerOf2,
    EncryptionTable,
)


# ---------------------------------------------------------------------------
# splitIntoValidPowersOf2
# ---------------------------------------------------------------------------

class TestSplitIntoValidPowersOf2:
    """Tests for splitIntoValidPowersOf2(n)."""

    def test_single_bit_one(self):
        assert splitIntoValidPowersOf2(1) == [1]

    def test_single_bit_two(self):
        assert splitIntoValidPowersOf2(2) == [2]

    def test_single_bit_four(self):
        assert splitIntoValidPowersOf2(4) == [4]

    def test_single_bit_eight(self):
        assert splitIntoValidPowersOf2(8) == [8]

    def test_single_bit_large_power(self):
        assert splitIntoValidPowersOf2(16) == [16]

    def test_two_bits_three(self):
        """3 = 1 + 2"""
        assert splitIntoValidPowersOf2(3) == [1, 2]

    def test_two_bits_five(self):
        """5 = 1 + 4"""
        assert splitIntoValidPowersOf2(5) == [1, 4]

    def test_two_bits_six(self):
        """6 = 2 + 4"""
        assert splitIntoValidPowersOf2(6) == [2, 4]

    def test_two_bits_ten(self):
        """10 = 2 + 8"""
        assert splitIntoValidPowersOf2(10) == [2, 8]

    def test_three_bits_seven(self):
        """7 = 1 + 2 + 4"""
        assert splitIntoValidPowersOf2(7) == [1, 2, 4]

    def test_four_bits_fifteen(self):
        """15 = 1 + 2 + 4 + 8"""
        assert splitIntoValidPowersOf2(15) == [1, 2, 4, 8]

    def test_result_sums_to_n(self):
        """The returned powers must always sum to n."""
        for n in [1, 3, 5, 7, 13, 17, 100, 173, 255]:
            parts = splitIntoValidPowersOf2(n)
            assert sum(parts) == n, f"sum({parts}) != {n}"

    def test_result_contains_only_powers_of_two(self):
        """Every element must be a power of 2."""
        for n in [6, 7, 10, 15, 173]:
            for val in splitIntoValidPowersOf2(n):
                assert val > 0 and (val & (val - 1)) == 0, f"{val} is not a power of 2"

    def test_result_is_sorted_ascending(self):
        """Powers are returned in ascending order."""
        for n in [7, 15, 173]:
            parts = splitIntoValidPowersOf2(n)
            assert parts == sorted(parts)

    def test_no_duplicates(self):
        """No duplicate powers in the result."""
        for n in [7, 10, 15, 173]:
            parts = splitIntoValidPowersOf2(n)
            assert len(parts) == len(set(parts))

    def test_large_exponent_173(self):
        """173 = 128 + 32 + 8 + 4 + 1"""
        assert splitIntoValidPowersOf2(173) == [1, 4, 8, 32, 128]


# ---------------------------------------------------------------------------
# getHighestPowerOf2
# ---------------------------------------------------------------------------

class TestGetHighestPowerOf2:
    """Tests for getHighestPowerOf2(n)."""

    def test_one(self):
        assert getHighestPowerOf2(1) == 1

    def test_two(self):
        assert getHighestPowerOf2(2) == 2

    def test_three(self):
        """floor(log2(3)) = 1, so 2^1 = 2"""
        assert getHighestPowerOf2(3) == 2

    def test_four(self):
        assert getHighestPowerOf2(4) == 4

    def test_five(self):
        assert getHighestPowerOf2(5) == 4

    def test_six(self):
        assert getHighestPowerOf2(6) == 4

    def test_seven(self):
        assert getHighestPowerOf2(7) == 4

    def test_eight(self):
        assert getHighestPowerOf2(8) == 8

    def test_nine(self):
        assert getHighestPowerOf2(9) == 8

    def test_sixteen(self):
        assert getHighestPowerOf2(16) == 16

    def test_result_is_power_of_two(self):
        """Result must always be a power of 2."""
        for n in [1, 3, 5, 7, 9, 13, 17, 100, 173]:
            result = getHighestPowerOf2(n)
            assert result > 0 and (result & (result - 1)) == 0

    def test_result_leq_n(self):
        """Result must be <= n."""
        for n in [1, 2, 5, 7, 10, 100, 173]:
            assert getHighestPowerOf2(n) <= n

    def test_result_times_two_gt_n(self):
        """2 * result must be > n (it is the largest power of 2 <= n)."""
        for n in [3, 5, 6, 7, 9, 13, 17, 100, 173]:
            result = getHighestPowerOf2(n)
            assert result * 2 > n


# ---------------------------------------------------------------------------
# EncryptionTable
# ---------------------------------------------------------------------------

class TestEncryptionTableInit:
    """Tests for EncryptionTable initialisation."""

    def test_exponent_1_power_list(self):
        et = EncryptionTable(1)
        assert et.power == [1]

    def test_exponent_1_validity(self):
        et = EncryptionTable(1)
        assert et.validity == [True]

    def test_exponent_2_power_list(self):
        et = EncryptionTable(2)
        assert et.power == [2]

    def test_exponent_2_validity(self):
        et = EncryptionTable(2)
        assert et.validity == [True]

    def test_exponent_3_power_list(self):
        """3 is odd, so start from 1; highest power = 2."""
        et = EncryptionTable(3)
        assert et.power == [1, 2]

    def test_exponent_3_validity(self):
        """3 = 1 + 2 → both rows valid."""
        et = EncryptionTable(3)
        assert et.validity == [True, True]

    def test_exponent_4_power_list(self):
        """4 is even → start from 2; highest power = 4 → power=[2,4]."""
        et = EncryptionTable(4)
        assert et.power == [2, 4]

    def test_exponent_4_validity(self):
        """4 = only power 4 is valid; power-2 row is included but invalid."""
        et = EncryptionTable(4)
        assert et.validity == [False, True]

    def test_exponent_8_power_list(self):
        """8 is even → start from 2; rows for 2, 4, 8 are generated."""
        et = EncryptionTable(8)
        assert et.power == [2, 4, 8]

    def test_exponent_8_validity(self):
        """8 = only power 8 valid; rows for 2 and 4 are invalid."""
        et = EncryptionTable(8)
        assert et.validity == [False, False, True]

    def test_exponent_5_power_list(self):
        """5 is odd; start from 1; highest = 4."""
        et = EncryptionTable(5)
        assert et.power == [1, 2, 4]

    def test_exponent_5_validity(self):
        """5 = 1 + 4 → index 0 (power 1) and index 2 (power 4) valid."""
        et = EncryptionTable(5)
        assert et.validity == [True, False, True]

    def test_exponent_6_power_list(self):
        """6 is even; start from 2; highest = 4."""
        et = EncryptionTable(6)
        assert et.power == [2, 4]

    def test_exponent_6_validity(self):
        """6 = 2 + 4 → both valid."""
        et = EncryptionTable(6)
        assert et.validity == [True, True]

    def test_exponent_7_power_list(self):
        et = EncryptionTable(7)
        assert et.power == [1, 2, 4]

    def test_exponent_7_all_valid(self):
        """7 = 1 + 2 + 4 → all rows valid."""
        et = EncryptionTable(7)
        assert et.validity == [True, True, True]

    def test_initial_prevSQR_zeros(self):
        et = EncryptionTable(7)
        assert et.prevSQR == [0, 0, 0]

    def test_initial_modNum_zeros(self):
        et = EncryptionTable(7)
        assert et.modNum == [0, 0, 0]

    def test_power_list_all_powers_of_two(self):
        for n in [1, 5, 7, 13, 17, 173]:
            et = EncryptionTable(n)
            for p in et.power:
                assert p > 0 and (p & (p - 1)) == 0

    def test_power_list_ascending(self):
        for n in [5, 7, 13, 17, 173]:
            et = EncryptionTable(n)
            assert et.power == sorted(et.power)


class TestEncryptionTableGetLength:
    """Tests for EncryptionTable.getLength()."""

    def test_exponent_1(self):
        assert EncryptionTable(1).getLength() == 1

    def test_exponent_2(self):
        assert EncryptionTable(2).getLength() == 1

    def test_exponent_3(self):
        assert EncryptionTable(3).getLength() == 2

    def test_exponent_7(self):
        assert EncryptionTable(7).getLength() == 3

    def test_length_equals_power_list_length(self):
        for n in [1, 5, 6, 7, 17, 173]:
            et = EncryptionTable(n)
            assert et.getLength() == len(et.power)


class TestEncryptionTableSetters:
    """Tests for setPrevSQR and setModNum."""

    def test_set_prevSQR_at_index_0(self):
        et = EncryptionTable(7)
        et.setPrevSQR(65, 0)
        assert et.prevSQR[0] == 65

    def test_set_prevSQR_at_index_1(self):
        et = EncryptionTable(7)
        et.setPrevSQR(1024, 1)
        assert et.prevSQR[1] == 1024

    def test_set_modNum_at_index_0(self):
        et = EncryptionTable(7)
        et.setModNum(32, 0)
        assert et.modNum[0] == 32

    def test_set_modNum_at_index_2(self):
        et = EncryptionTable(7)
        et.setModNum(1, 2)
        assert et.modNum[2] == 1

    def test_set_and_overwrite(self):
        et = EncryptionTable(3)
        et.setModNum(10, 0)
        et.setModNum(20, 0)
        assert et.modNum[0] == 20


class TestEncryptionTableGetProduct:
    """Tests for getProduct()."""

    def test_exponent_7_all_valid_product(self):
        """E=7, all rows valid: product = m0 * m1 * m2."""
        et = EncryptionTable(7)
        et.setModNum(32, 0)
        et.setModNum(1, 1)
        et.setModNum(1, 2)
        assert et.getProduct() == 32

    def test_exponent_5_partial_validity(self):
        """E=5: power [1,2,4], validity [T,F,T]. Product = m0 * m2."""
        et = EncryptionTable(5)
        et.setModNum(65, 0)
        et.setModNum(999, 1)  # row 1 is NOT valid; should be ignored
        et.setModNum(3, 2)
        assert et.getProduct() == 65 * 3

    def test_exponent_6_two_valid_rows(self):
        """E=6: power [2,4], validity [T,T]. Product = m0 * m1."""
        et = EncryptionTable(6)
        et.setModNum(7, 0)
        et.setModNum(3, 1)
        assert et.getProduct() == 21

    def test_product_when_all_modNums_zero(self):
        """Default modNums are 0; product over valid rows is 0 (for n>1)."""
        et = EncryptionTable(3)
        # Both rows valid, both modNums = 0 → 0 * 0 = 0
        assert et.getProduct() == 0

    def test_single_valid_row_product_equals_that_modNum(self):
        """EncryptionTable(1): power=[1], validity=[True] → exactly one row."""
        et = EncryptionTable(1)
        et.setModNum(42, 0)
        assert et.getProduct() == 42

