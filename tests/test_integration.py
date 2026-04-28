"""
End-to-end integration tests for encrypt() ↔ decrypt() round-trips.

These tests verify the full pipeline using a variety of key sets,
message types, and edge cases — exercising Encryption → EncryptionTable,
Decryption → DecryptionTable → DTable all together.
"""
import pytest
from npcryption import encrypt, decrypt

# Key sets where N > 127: all printable ASCII (32–126) can be encrypted.
SAFE_KEY_SETS = [
    (17, 19, 5),    # N=323  (3-digit blocks)
    (61, 53, 17),   # N=3233 (4-digit blocks)
    (11, 13, 7),    # N=143  (3-digit blocks)
]

# Key sets with small N: only characters with ord(ch) < N are valid inputs.
# (7, 13): N=91  — safe for ASCII < 91 (e.g. digits, A-Z, most punctuation)
# (5, 11): N=55  — safe for ASCII < 55 (e.g. '!' through '6')
SMALL_KEY_SETS = [
    (7,  13, 5),    # N=91
    (5,  11, 3),    # N=55
]

# All key sets combined (used only where the message chars are guaranteed
# to have ord < min(N) across the set, i.e. ord < 55).
ALL_KEY_SETS = SAFE_KEY_SETS + SMALL_KEY_SETS


class TestRoundTrip:
    """Encrypt then decrypt must recover the original plaintext."""

    @pytest.mark.parametrize("P,Q,E", ALL_KEY_SETS)
    def test_single_char_A(self, P, Q, E):
        # 'A' = ASCII 65; skip key sets where N ≤ 65.
        if P * Q <= 65:
            pytest.skip(f"N={P * Q} too small for 'A' (ASCII 65)")
        msg = 'A'
        assert decrypt(P, Q, E, encrypt(P, Q, E, msg)) == msg

    @pytest.mark.parametrize("P,Q,E", ALL_KEY_SETS)
    def test_single_char_space(self, P, Q, E):
        # space = ASCII 32; skip key sets where N ≤ 32.
        if P * Q <= 32:
            pytest.skip(f"N={P * Q} too small for space (ASCII 32)")
        msg = ' '
        assert decrypt(P, Q, E, encrypt(P, Q, E, msg)) == msg

    @pytest.mark.parametrize("P,Q,E", ALL_KEY_SETS)
    def test_empty_string(self, P, Q, E):
        assert decrypt(P, Q, E, encrypt(P, Q, E, '')) == ''

    @pytest.mark.parametrize("P,Q,E", SAFE_KEY_SETS)
    def test_hello(self, P, Q, E):
        msg = 'Hello'
        assert decrypt(P, Q, E, encrypt(P, Q, E, msg)) == msg

    @pytest.mark.parametrize("P,Q,E", SAFE_KEY_SETS)
    def test_hello_world(self, P, Q, E):
        msg = 'Hello World'
        assert decrypt(P, Q, E, encrypt(P, Q, E, msg)) == msg

    @pytest.mark.parametrize("P,Q,E", SAFE_KEY_SETS)
    def test_repeated_character(self, P, Q, E):
        msg = 'aaaa'
        assert decrypt(P, Q, E, encrypt(P, Q, E, msg)) == msg

    @pytest.mark.parametrize("P,Q,E", SAFE_KEY_SETS)
    def test_all_same_block_in_cipher(self, P, Q, E):
        """Repeated chars → identical cipher blocks → single decrypt cache hit."""
        msg = 'BBBB'
        cipher = encrypt(P, Q, E, msg)
        block_len = len(str(P * Q))
        # All 4 blocks must be identical
        blocks = [cipher[i:i + block_len] for i in range(0, len(cipher), block_len)]
        assert len(set(blocks)) == 1
        assert decrypt(P, Q, E, cipher) == msg

    @pytest.mark.parametrize("P,Q,E", SAFE_KEY_SETS)
    def test_digits_in_message(self, P, Q, E):
        msg = '1234'
        assert decrypt(P, Q, E, encrypt(P, Q, E, msg)) == msg

    @pytest.mark.parametrize("P,Q,E", SAFE_KEY_SETS)
    def test_mixed_case(self, P, Q, E):
        msg = 'AbCdEf'
        assert decrypt(P, Q, E, encrypt(P, Q, E, msg)) == msg

    @pytest.mark.parametrize("P,Q,E", SAFE_KEY_SETS)
    def test_punctuation(self, P, Q, E):
        msg = '!@#$'
        assert decrypt(P, Q, E, encrypt(P, Q, E, msg)) == msg

    @pytest.mark.parametrize("P,Q,E", SAFE_KEY_SETS)
    def test_sentence_with_punctuation(self, P, Q, E):
        msg = 'Test, okay?'
        assert decrypt(P, Q, E, encrypt(P, Q, E, msg)) == msg


class TestCipherProperties:
    """Tests that verify structural properties of the ciphertext."""

    def test_cipher_is_string(self):
        assert isinstance(encrypt(17, 19, 5, 'Hi'), str)

    def test_cipher_is_all_digits(self):
        assert encrypt(17, 19, 5, 'Hello World!').isdigit()

    def test_cipher_length_is_n_times_block_width(self):
        P, Q, E = 17, 19, 5
        msg = 'Hello'
        cipher = encrypt(P, Q, E, msg)
        assert len(cipher) == len(msg) * len(str(P * Q))

    def test_cipher_length_4digit_modulus(self):
        P, Q, E = 61, 53, 17
        msg = 'Hi'
        cipher = encrypt(P, Q, E, msg)
        assert len(cipher) == 2 * 4  # 2 chars, 4-digit N

    def test_cipher_length_2digit_modulus(self):
        P, Q, E = 7, 13, 5
        msg = 'AB'
        cipher = encrypt(P, Q, E, msg)
        assert len(cipher) == 2 * 2  # 2 chars, 2-digit N

    def test_each_block_integer_less_than_N(self):
        """C < N must hold for every cipher block."""
        P, Q, E = 17, 19, 5
        N = P * Q
        block_len = len(str(N))
        msg = 'Hello World!'
        cipher = encrypt(P, Q, E, msg)
        for i in range(0, len(cipher), block_len):
            block_val = int(cipher[i:i + block_len])
            assert block_val < N

    def test_different_chars_different_blocks(self):
        """Different characters (in the same message) produce different cipher blocks."""
        P, Q, E = 17, 19, 5
        a_block = encrypt(P, Q, E, 'A')
        b_block = encrypt(P, Q, E, 'B')
        assert a_block != b_block

    def test_different_keys_different_ciphers(self):
        """Same message, different keys → different ciphertext."""
        msg = 'Hi'
        c1 = encrypt(17, 19, 5, msg)
        c2 = encrypt(61, 53, 17, msg)
        # N values differ so block lengths differ, but we also check numeric values
        assert c1 != c2

    def test_ciphertext_not_equal_to_plaintext(self):
        """For typical inputs, ciphertext should not equal plaintext."""
        msg = 'Hello'
        cipher = encrypt(17, 19, 5, msg)
        assert cipher != msg


class TestCachingBehavior:
    """Verify the in-memory character caching does not affect correctness."""

    def test_cache_hits_on_repeated_chars(self):
        """'aaabbbccc' has repeated chars; round-trip must still work."""
        msg = 'aaabbbccc'
        assert decrypt(17, 19, 5, encrypt(17, 19, 5, msg)) == msg

    def test_same_char_at_start_and_end(self):
        msg = 'H' + 'World' + 'H'  # 'HWorldH'
        assert decrypt(17, 19, 5, encrypt(17, 19, 5, msg)) == msg

    def test_all_same_character(self):
        msg = 'X' * 10
        assert decrypt(17, 19, 5, encrypt(17, 19, 5, msg)) == msg

    def test_alternating_two_chars(self):
        msg = 'ABABAB'
        assert decrypt(17, 19, 5, encrypt(17, 19, 5, msg)) == msg


class TestSmallKeySetRoundTrip:
    """Round-trip tests for small-N key sets using only low-ASCII characters."""

    def test_space_with_N91(self):
        """N=91 > 32 (space), so space round-trips correctly."""
        assert decrypt(7, 13, 5, encrypt(7, 13, 5, ' ')) == ' '

    def test_exclamation_with_N91(self):
        """'!' = ASCII 33 < 91."""
        assert decrypt(7, 13, 5, encrypt(7, 13, 5, '!')) == '!'

    def test_digits_with_N91(self):
        """Digits 0-9 (ASCII 48-57) < 91."""
        msg = '0123456789'
        assert decrypt(7, 13, 5, encrypt(7, 13, 5, msg)) == msg

    def test_uppercase_A_to_Z_with_N91(self):
        """A-Z (65-90) < 91."""
        msg = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        assert decrypt(7, 13, 5, encrypt(7, 13, 5, msg)) == msg

    def test_space_with_N55(self):
        """N=55 > 32 (space)."""
        assert decrypt(5, 11, 3, encrypt(5, 11, 3, ' ')) == ' '

    def test_exclamation_with_N55(self):
        """'!' = ASCII 33 < 55."""
        assert decrypt(5, 11, 3, encrypt(5, 11, 3, '!')) == '!'

    def test_low_ascii_range_N55(self):
        """Characters with ASCII 32-54 (inclusive) are safe for N=55."""
        msg = ''.join(chr(c) for c in range(32, 55))
        assert decrypt(5, 11, 3, encrypt(5, 11, 3, msg)) == msg


class TestAllPrintableASCII:
    """Round-trip test for every printable ASCII character (32-126)."""

    def test_all_printable_ascii(self):
        P, Q, E = 17, 19, 5
        for code in range(32, 127):
            ch = chr(code)
            cipher = encrypt(P, Q, E, ch)
            plain = decrypt(P, Q, E, cipher)
            assert plain == ch, f"Round-trip failed for ASCII {code} ({repr(ch)})"

    def test_all_printable_ascii_long_message(self):
        """Concatenate all printable chars as one message."""
        P, Q, E = 17, 19, 5
        msg = ''.join(chr(c) for c in range(32, 127))
        cipher = encrypt(P, Q, E, msg)
        plain = decrypt(P, Q, E, cipher)
        assert plain == msg

