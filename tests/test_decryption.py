"""
Tests for npcryption.core.Decryption module.

Covers:
  - getAscii()
  - getCharacter()
  - decryptCharacter()
  - decrypt() — including empty string, single block, multi-block,
    repeated blocks (caching), correct block parsing
"""
from npcryption.core.Decryption import decrypt, decryptCharacter, getAscii, getCharacter
from npcryption.core.DecryptionTable import DecryptionTable
from npcryption.core.Encryption import encrypt

# ---------------------------------------------------------------------------
# Key parameters
# P=17, Q=19, E=5:  N=323, phi=288, D=173
# P=61, Q=53, E=17: N=3233, phi=3120
# P=7,  Q=13, E=5:  N=91,   phi=72
# ---------------------------------------------------------------------------

P17, Q19, E5 = 17, 19, 5
P61, Q53, E17 = 61, 53, 17
P7, Q13 = 7, 13


class TestDecryptionGetAscii:
    """Tests for getAscii in Decryption module (same as Encryption)."""

    def test_A(self):
        assert getAscii('A') == 65

    def test_space(self):
        assert getAscii(' ') == 32

    def test_matches_ord(self):
        for ch in 'Hello!':
            assert getAscii(ch) == ord(ch)


class TestDecryptionGetCharacter:
    """Tests for getCharacter in Decryption module."""

    def test_65_is_A(self):
        assert getCharacter(65) == 'A'

    def test_32_is_space(self):
        assert getCharacter(32) == ' '

    def test_matches_chr(self):
        for code in [33, 48, 65, 90, 97, 122]:
            assert getCharacter(code) == chr(code)


class TestDecryptCharacter:
    """Tests for decryptCharacter(PQ, codedChar, powers)."""

    def _make_table(self, phi, E):
        return DecryptionTable(phi, E)

    def test_returns_string(self):
        table = self._make_table((P17 - 1) * (Q19 - 1), E5)
        result = decryptCharacter(P17 * Q19, 21, table)
        assert isinstance(result, str)

    def test_H_block_21_decrypts_to_H(self):
        """encrypt(17,19,5,'H')='021' → codedChar=21 → 'H'."""
        table = self._make_table((P17 - 1) * (Q19 - 1), E5)
        assert decryptCharacter(P17 * Q19, 21, table) == 'H'

    def test_A_block_12_decrypts_to_A(self):
        """encrypt(17,19,5,'A')='012' → codedChar=12 → 'A'."""
        table = self._make_table((P17 - 1) * (Q19 - 1), E5)
        assert decryptCharacter(P17 * Q19, 12, table) == 'A'

    def test_result_is_single_character(self):
        table = self._make_table((P17 - 1) * (Q19 - 1), E5)
        result = decryptCharacter(P17 * Q19, 21, table)
        assert len(result) == 1

    def test_all_encrypted_blocks_decrypt_correctly(self):
        """For every letter A-Z, decryptCharacter should reverse encryptCharacter."""
        PQ = P17 * Q19
        phi = (P17 - 1) * (Q19 - 1)
        from npcryption.core.Encryption import encryptCharacter
        from npcryption.core.EncryptionTable import EncryptionTable
        for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            et = EncryptionTable(E5)
            cipher_str = encryptCharacter(PQ, ch, et)
            coded_int = int(cipher_str)
            dec_table2 = self._make_table(phi, E5)
            plain = decryptCharacter(PQ, coded_int, dec_table2)
            assert plain == ch, f"Failed for '{ch}'"


class TestDecrypt:
    """Tests for decrypt(P, Q, E, message)."""

    # --- Output type ---

    def test_returns_string(self):
        cipher = encrypt(P17, Q19, E5, 'A')
        result = decrypt(P17, Q19, E5, cipher)
        assert isinstance(result, str)

    # --- Empty string ---

    def test_empty_ciphertext_returns_empty(self):
        assert decrypt(P17, Q19, E5, '') == ''

    # --- Known ciphertext → plaintext ---

    def test_decrypt_known_H_block(self):
        """Cipher '021' (for 'H') should decrypt to 'H'."""
        assert decrypt(P17, Q19, E5, '021') == 'H'

    def test_decrypt_known_A_block(self):
        assert decrypt(P17, Q19, E5, '012') == 'A'

    def test_decrypt_hello_world(self):
        cipher = '021271109109042223083042190109104067'
        assert decrypt(P17, Q19, E5, cipher) == 'Hello World!'

    def test_decrypt_small_keys_AB(self):
        """Known: encrypt(7,13,5,'AB')='3940'."""
        assert decrypt(P7, Q13, E5, '3940') == 'AB'

    def test_decrypt_large_keys_Hi(self):
        """Known: encrypt(61,53,17,'Hi')='30003179'."""
        assert decrypt(P61, Q53, E17, '30003179') == 'Hi'

    # --- Block parsing ---

    def test_block_parsing_uses_len_of_N(self):
        """Cipher is split into chunks of len(str(N)) digits."""
        # N=323 → 3-digit blocks; '021271' → ['021','271'] → ['H','?']
        c = encrypt(P17, Q19, E5, 'He')
        assert len(c) == 6
        plain = decrypt(P17, Q19, E5, c)
        assert plain == 'He'

    # --- Caching (repeated blocks) ---

    def test_repeated_blocks_use_cache(self):
        """'aaa' produces the same cipher block 3 times."""
        cipher = encrypt(P17, Q19, E5, 'aaa')
        plain = decrypt(P17, Q19, E5, cipher)
        assert plain == 'aaa'

    # --- Correctness across characters ---

    def test_single_char_all_printable(self):
        """decrypt(encrypt(ch)) == ch for all printable ASCII."""
        for code in range(32, 127):
            ch = chr(code)
            cipher = encrypt(P17, Q19, E5, ch)
            plain = decrypt(P17, Q19, E5, cipher)
            assert plain == ch, f"Round-trip failed for {repr(ch)}"

    # --- Determinism ---

    def test_same_inputs_same_output(self):
        cipher = encrypt(P17, Q19, E5, 'test')
        r1 = decrypt(P17, Q19, E5, cipher)
        r2 = decrypt(P17, Q19, E5, cipher)
        assert r1 == r2

    # --- Multiple keys ---

    def test_decrypt_with_wrong_keys_gives_wrong_result(self):
        """Decrypting with different keys should not recover the original plaintext."""
        msg = 'Hello'
        cipher = encrypt(P17, Q19, E5, msg)
        wrong_plain = decrypt(P61, Q53, E17, cipher)
        # The char count will differ (different block widths), so this
        # just checks that we don't accidentally get the right answer.
        assert wrong_plain != msg

    def test_long_message_round_trip_via_decrypt(self):
        """decrypt(encrypt(msg)) == msg for a long message."""
        msg = 'The quick brown fox!'
        cipher = encrypt(P17, Q19, E5, msg)
        assert decrypt(P17, Q19, E5, cipher) == msg
