"""
Tests for web/demo.py, the bridge the website uses to call NPcryption.

The demo reads the library's intermediate tables (EncryptionTable rows,
DTable columns), so these tests catch library changes that would break
the website.
"""
import importlib.util
import json
import os

from npcryption import decrypt, encrypt
from npcryption.core.DecryptionTable import DecryptionTable

_DEMO = os.path.join(os.path.dirname(__file__), '..', 'web', 'demo.py')
_spec = importlib.util.spec_from_file_location('npcryption_web_demo', _DEMO)
demo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(demo)


class TestKeys:

    def test_derives_n_phi_and_d(self):
        key = demo.keys(17, 19, 5)
        assert key['errors'] == {}
        assert (key['n'], key['phi'], key['d'], key['width']) == (323, 288, 173, 3)

    def test_d_matches_library(self):
        assert demo.keys(61, 53, 17)['d'] == DecryptionTable.getD(3120, 17)

    def test_euclid_rows_match_documented_table(self):
        rows = demo.keys(17, 19, 5)['euclid']
        assert [row['r'] for row in rows] == [288, 5, 3, 2, 1]
        assert [row['d'] for row in rows] == [0, 1, -57, 58, -115]

    def test_exponent_choices_are_coprime_with_phi(self):
        choices = demo.keys(17, 19, 5)['choices']
        assert choices[:4] == [5, 7, 11, 13]
        assert len(choices) == demo.EXPONENT_CHOICES

    def test_rejects_composite_prime(self):
        assert demo.keys(21, 19, 5)['errors']['p'] == "21 isn't prime: it's 3 × 7."

    def test_rejects_equal_primes(self):
        assert 'q' in demo.keys(17, 17, 5)['errors']

    def test_rejects_out_of_range_prime(self):
        assert 'q' in demo.keys(17, 10007, 5)['errors']

    def test_rejects_exponent_sharing_factor_with_phi(self):
        assert 'shares the factor 3' in demo.keys(17, 19, 3)['errors']['e']

    def test_rejects_primes_with_no_exponent(self):
        assert 'e' in demo.keys(2, 3, 5)['errors']


class TestEncryptSteps:

    def test_ciphertext_matches_library(self):
        result = demo.encrypt_steps(17, 19, 5, 'Hello, RSA!')
        assert result['ciphertext'] == encrypt(17, 19, 5, 'Hello, RSA!')
        assert ''.join(c['block'] for c in result['chars']) == result['ciphertext']

    def test_ladder_for_documented_example(self):
        h = demo.encrypt_steps(17, 19, 5, 'H')['chars'][0]
        assert (h['code'], h['block'], h['product']) == (72, '021', '18432')
        assert [row['value'] for row in h['ladder']] == ['72', '16', '256']
        assert [row['used'] for row in h['ladder']] == [True, False, True]

    def test_flags_characters_too_large_for_n(self):
        chars = demo.encrypt_steps(5, 11, 3, 'A!')['chars']
        assert [c['fits'] for c in chars] == [False, True]

    def test_truncates_long_messages(self):
        result = demo.encrypt_steps(17, 19, 5, 'x' * 100)
        assert len(result['chars']) == demo.MAX_MESSAGE

    def test_invalid_keys_return_only_errors(self):
        assert set(demo.encrypt_steps(4, 19, 5, 'Hi')) == {'keys'}


class TestDecryptSteps:

    def test_round_trip(self):
        cipher = encrypt(61, 53, 17, 'Hello, World!')
        result = demo.decrypt_steps(61, 53, 17, cipher)
        assert result['plaintext'] == decrypt(61, 53, 17, cipher) == 'Hello, World!'
        assert len(result['blocks'][0]['ladder']) == demo.keys(61, 53, 17)['d'].bit_length()

    def test_ignores_spaces_between_blocks(self):
        assert demo.decrypt_steps(17, 19, 5, '021 022')['plaintext'] == 'Hi'

    def test_rejects_non_digits(self):
        assert 'only contain digits' in demo.decrypt_steps(17, 19, 5, '02a')['error']

    def test_rejects_partial_blocks(self):
        assert '3-digit blocks' in demo.decrypt_steps(17, 19, 5, '0210')['error']

    def test_unreadable_block_has_no_character(self):
        # With N above 0x10FFFF, an arbitrary block can decrypt past the last code point.
        result = demo.decrypt_steps(9973, 9967, 5, '12345678')
        assert result['blocks'][0]['code'] > 0x10FFFF
        assert result['blocks'][0]['char'] is None
        assert result['plaintext'] is None


class TestCrackAndCall:

    def test_crack_recovers_private_exponent(self):
        result = demo.crack(17, 19, 5)
        assert (result['factor'], result['other'], result['d']) == (17, 19, 173)

    def test_call_returns_json(self):
        assert json.loads(demo.call('keys', 17, 19, 5))['d'] == 173
        assert json.loads(demo.call('info'))['version']
