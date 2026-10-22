"""
Tests for the npcryption package public API.

Covers:
  - __version__
  - __all__
  - Top-level encrypt() and decrypt() are importable and functional
  - Package metadata consistency
"""
from importlib import metadata

import pytest

import npcryption
from npcryption import encrypt, decrypt


class TestPackageVersion:
    """Tests for npcryption.__version__."""

    def test_version_exists(self):
        assert hasattr(npcryption, '__version__')

    def test_version_is_string(self):
        assert isinstance(npcryption.__version__, str)

    def test_version_matches_package_metadata(self):
        """pyproject.toml takes its version from __version__, so they must agree."""
        try:
            installed = metadata.version('npcryption')
        except metadata.PackageNotFoundError:
            pytest.skip('npcryption is not installed')
        assert installed == npcryption.__version__, (
            'Installed metadata is stale; reinstall with `pip install -e .`')

    def test_version_format(self):
        """Version should follow 'X.Y.Z' semver pattern."""
        parts = npcryption.__version__.split('.')
        assert len(parts) == 3
        for part in parts:
            assert part.isdigit(), f"Non-numeric version component: {part}"


class TestPackageAll:
    """Tests for npcryption.__all__."""

    def test_all_exists(self):
        assert hasattr(npcryption, '__all__')

    def test_all_is_list(self):
        assert isinstance(npcryption.__all__, list)

    def test_all_contains_encrypt(self):
        assert 'encrypt' in npcryption.__all__

    def test_all_contains_decrypt(self):
        assert 'decrypt' in npcryption.__all__

    def test_all_has_exactly_two_entries(self):
        assert len(npcryption.__all__) == 2


class TestPublicEncrypt:
    """Tests for the top-level encrypt() re-exported by __init__.py."""

    def test_importable_directly(self):
        from npcryption import encrypt as e
        assert callable(e)

    def test_returns_string(self):
        assert isinstance(encrypt(17, 19, 5, 'A'), str)

    def test_empty_message(self):
        assert encrypt(17, 19, 5, '') == ''

    def test_known_single_char(self):
        assert encrypt(17, 19, 5, 'H') == '021'

    def test_known_full_message(self):
        assert encrypt(17, 19, 5, 'Hello World!') == '021271109109042223083042190109104067'


class TestPublicDecrypt:
    """Tests for the top-level decrypt() re-exported by __init__.py."""

    def test_importable_directly(self):
        from npcryption import decrypt as d
        assert callable(d)

    def test_returns_string(self):
        cipher = encrypt(17, 19, 5, 'A')
        assert isinstance(decrypt(17, 19, 5, cipher), str)

    def test_empty_message(self):
        assert decrypt(17, 19, 5, '') == ''

    def test_known_cipher(self):
        assert decrypt(17, 19, 5, '021') == 'H'

    def test_round_trip(self):
        msg = 'Hello'
        assert decrypt(17, 19, 5, encrypt(17, 19, 5, msg)) == msg


class TestPublicAPIFunctionIdentity:
    """Verify that the package-level functions are the same objects as the core ones."""

    def test_encrypt_is_core_encrypt(self):
        from npcryption.core.Encryption import encrypt as core_encrypt
        assert encrypt is core_encrypt

    def test_decrypt_is_core_decrypt(self):
        from npcryption.core.Decryption import decrypt as core_decrypt
        assert decrypt is core_decrypt
