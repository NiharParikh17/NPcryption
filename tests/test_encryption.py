"""
Tests for npcryption.core.Encryption module.

Covers:
  - getAscii()
  - getCharacter()
  - encryptCharacter()
  - encrypt() — including empty string, single char, multi-char,
    repeated characters (caching), zero-padding, block width
"""
import pytest
from npcryption.core.Encryption import encrypt, encryptCharacter, getAscii, getCharacter
from npcryption.core.EncryptionTable import EncryptionTable

# ---------------------------------------------------------------------------
# Key parameters used across tests
# P=17, Q=19, E=5:  N=323,  phi=288, D=173
# P=61, Q=53, E=17: N=3233, phi=3120
# P=7,  Q=13, E=5:  N=91,   phi=72
# ---------------------------------------------------------------------------

P17, Q19, E5 = 17, 19, 5
P61, Q53, E17 = 61, 53, 17
P7, Q13 = 7, 13


class TestGetAscii:
    """Tests for getAscii(character)."""

    def test_uppercase_A(self):
        assert getAscii('A') == 65

    def test_uppercase_Z(self):
        assert getAscii('Z') == 90

    def test_lowercase_a(self):
        assert getAscii('a') == 97

    def test_space(self):
        assert getAscii(' ') == 32

    def test_exclamation(self):
        assert getAscii('!') == 33

    def test_digit_zero(self):
        assert getAscii('0') == 48

    def test_newline(self):
        assert getAscii('\n') == 10

    def test_matches_ord(self):
        for ch in 'Hello World!0123ABCxyz':
            assert getAscii(ch) == ord(ch)


class TestGetCharacter:
    """Tests for getCharacter(ascii)."""

    def test_65_is_A(self):
        assert getCharacter(65) == 'A'

    def test_97_is_a(self):
        assert getCharacter(97) == 'a'

    def test_32_is_space(self):
        assert getCharacter(32) == ' '

    def test_matches_chr(self):
        for code in [32, 33, 48, 65, 90, 97, 122]:
            assert getCharacter(code) == chr(code)

    def test_roundtrip_ascii_to_char(self):
        for ch in 'Hello World!':
            assert getCharacter(getAscii(ch)) == ch


class TestEncryptCharacter:
    """Tests for encryptCharacter(PQ, character, powers)."""

    def _make_table(self, E):
        return EncryptionTable(E)

    def test_output_is_string(self):
        table = self._make_table(E5)
        result = encryptCharacter(P17 * Q19, 'H', table)
        assert isinstance(result, str)

    def test_block_width_equals_len_of_PQ(self):
        PQ = P17 * Q19  # 323, len=3
        table = self._make_table(E5)
        result = encryptCharacter(PQ, 'H', table)
        assert len(result) == len(str(PQ))

    def test_block_width_4digit_modulus(self):
        PQ = P61 * Q53  # 3233, len=4
        table = self._make_table(E17)
        result = encryptCharacter(PQ, 'H', table)
        assert len(result) == 4

    def test_H_encrypted_with_E5_N323(self):
        """Known value from exploration: encryptCharacter(323, 'H', E=5)='021'."""
        table = self._make_table(E5)
        assert encryptCharacter(323, 'H', table) == '021'

    def test_A_encrypted_with_E5_N323(self):
        """Known value: encrypt(17,19,5,'A')='012'."""
        table = self._make_table(E5)
        assert encryptCharacter(323, 'A', table) == '012'

    def test_output_is_zero_padded(self):
        """Numeric result must be zero-padded to len(str(PQ)) digits."""
        PQ = 323
        table = self._make_table(E5)
        result = encryptCharacter(PQ, 'A', table)
        assert len(result) == 3
        assert result.isdigit()

    def test_result_is_numeric_string(self):
        PQ = P17 * Q19
        table = self._make_table(E5)
        result = encryptCharacter(PQ, 'z', table)
        assert result.isdigit()

    def test_integer_value_less_than_PQ(self):
        """Ciphertext integer C must be < N = P*Q."""
        PQ = P17 * Q19
        table = self._make_table(E5)
        for ch in 'Hello!':
            result = encryptCharacter(PQ, ch, table)
            assert int(result) < PQ

    def test_same_char_same_table_same_result(self):
        """The same table instance produces the same result when called again."""
        PQ = P17 * Q19
        table = self._make_table(E5)
        r1 = encryptCharacter(PQ, 'A', table)
        table2 = self._make_table(E5)
        r2 = encryptCharacter(PQ, 'A', table2)
        assert r1 == r2


class TestEncrypt:
    """Tests for encrypt(P, Q, E, message)."""

    # --- Output type ---

    def test_returns_string(self):
        result = encrypt(P17, Q19, E5, 'A')
        assert isinstance(result, str)

    # --- Empty string ---

    def test_empty_string_returns_empty(self):
        assert encrypt(P17, Q19, E5, '') == ''

    # --- Single character ---

    def test_single_char_H(self):
        assert encrypt(P17, Q19, E5, 'H') == '021'

    def test_single_char_A(self):
        assert encrypt(P17, Q19, E5, 'A') == '012'

    # --- Block width ---

    def test_single_char_length_equals_len_N(self):
        """Each character produces exactly len(str(N)) digits."""
        N = P17 * Q19
        result = encrypt(P17, Q19, E5, 'Z')
        assert len(result) == len(str(N))

    def test_multi_char_length(self):
        """Length = num_chars * len(str(N))."""
        N = P17 * Q19
        msg = 'Hello'
        result = encrypt(P17, Q19, E5, msg)
        assert len(result) == len(msg) * len(str(N))

    def test_result_is_all_digits(self):
        result = encrypt(P17, Q19, E5, 'Hello World!')
        assert result.isdigit()

    # --- Known ciphertext values ---

    def test_hello_world_exclaim(self):
        expected = '021271109109042223083042190109104067'
        assert encrypt(P17, Q19, E5, 'Hello World!') == expected

    def test_two_char_AB_small_keys(self):
        """Known: encrypt(7, 13, 5, 'AB') = '3940'."""
        assert encrypt(P7, Q13, E5, 'AB') == '3940'

    def test_hi_large_keys(self):
        """Known: encrypt(61, 53, 17, 'Hi') = '30003179'."""
        assert encrypt(P61, Q53, E17, 'Hi') == '30003179'

    # --- Caching (repeated characters) ---

    def test_repeated_chars_use_cache(self):
        """Repeated char must produce the same block each time."""
        result = encrypt(P17, Q19, E5, 'aaa')
        block = result[:3]
        assert result == block * 3

    def test_repeated_chars_known_value(self):
        """Known: encrypt(17, 19, 5, 'aaa') = '241241241'."""
        assert encrypt(P17, Q19, E5, 'aaa') == '241241241'

    def test_cache_consistent_within_message(self):
        """Same char at different positions should produce the same block."""
        result = encrypt(P17, Q19, E5, 'aba')
        block_a = encrypt(P17, Q19, E5, 'a')
        block_b = encrypt(P17, Q19, E5, 'b')
        assert result == block_a + block_b + block_a

    # --- Determinism ---

    def test_same_inputs_same_output(self):
        r1 = encrypt(P17, Q19, E5, 'Hello')
        r2 = encrypt(P17, Q19, E5, 'Hello')
        assert r1 == r2

    def test_different_keys_different_ciphertext(self):
        c1 = encrypt(P17, Q19, E5, 'A')
        c2 = encrypt(P61, Q53, E17, 'A')
        assert c1 != c2

    # --- Zero-padding ---

    def test_zero_padding_present(self):
        """Cipher block must always be exactly len(str(N)) chars, possibly zero-padded."""
        N = P17 * Q19  # 323 → 3 digits
        result = encrypt(P17, Q19, E5, 'A')
        assert len(result) == 3
        # '012' starts with '0' → zero-padding is applied
        assert result[0] == '0'

    # --- All printable ASCII characters ---

    def test_all_printable_ascii_round_trip(self):
        """Every printable ASCII (32-126) should produce a fixed-width block."""
        N = P17 * Q19
        block_len = len(str(N))
        for code in range(32, 127):
            ch = chr(code)
            c = encrypt(P17, Q19, E5, ch)
            assert len(c) == block_len, f"Block width wrong for char {repr(ch)}"
            assert c.isdigit(), f"Non-digit in cipher for char {repr(ch)}"

    # --- Spaces and special characters ---

    def test_space_character(self):
        result = encrypt(P17, Q19, E5, ' ')
        assert len(result) == 3
        assert result.isdigit()

    def test_newline_character(self):
        result = encrypt(P17, Q19, E5, '\n')
        assert len(result) == 3

    # --- Long message ---

    def test_long_message_correct_length(self):
        msg = 'The quick brown fox jumps over the lazy dog.'
        N = P17 * Q19
        result = encrypt(P17, Q19, E5, msg)
        assert len(result) == len(msg) * len(str(N))

