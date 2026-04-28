"""
Tests for npcryption.cli module.

The cli.py file has two design constraints that tests must work around:
  1. It uses bare imports (`import Encryption`, `import Decryption`) which
     only resolve when the core/ directory is on sys.path.
  2. It calls `main()` at module level, so importing the module triggers
     interactive input prompts.

Strategy:
  - Pre-patch sys.modules with the real core modules so the bare imports
    resolve.
  - Pre-patch builtins.input before importing the module so the `main()`
    call that runs at import time does not block.
  - Reload the module for each test that needs a clean state.

NOTE: Because of the module-level `main()` call, some tests verify the
output produced *during import* by capturing stdout.
"""
import sys
import importlib
import importlib.util
import types
from io import StringIO
from unittest.mock import patch, MagicMock
import pytest
import npcryption.core.Encryption as _enc_mod
import npcryption.core.Decryption as _dec_mod


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_cli(input_side_effects):
    """
    Load (or reload) npcryption.cli with builtins.input replaced by a mock
    that returns values from *input_side_effects* in order.

    The core Encryption / Decryption modules are injected into sys.modules
    under the bare names expected by cli.py.
    """
    # Inject bare-name aliases so `import Encryption` / `import Decryption`
    # in cli.py resolve to the proper package modules.
    sys.modules.setdefault('Encryption', _enc_mod)
    sys.modules.setdefault('Decryption', _dec_mod)

    # Remove any cached version so we get a fresh import.
    sys.modules.pop('npcryption.cli', None)

    with patch('builtins.input', side_effect=input_side_effects):
        import npcryption.cli as cli
    return cli


# ---------------------------------------------------------------------------
# Tests for cli.encrypt wrapper
# ---------------------------------------------------------------------------

class TestCliEncryptWrapper:
    """cli.encrypt() is a thin wrapper around Encryption.encrypt."""

    def test_returns_string(self):
        cli = _load_cli(['E', '17', '19', '5', 'A'])
        result = cli.encrypt(17, 19, 5, 'A')
        assert isinstance(result, str)

    def test_known_value(self):
        cli = _load_cli(['E', '17', '19', '5', 'H'])
        assert cli.encrypt(17, 19, 5, 'H') == '021'

    def test_empty_message(self):
        cli = _load_cli(['E', '17', '19', '5', ''])
        assert cli.encrypt(17, 19, 5, '') == ''

    def test_delegates_to_core(self):
        cli = _load_cli(['E', '17', '19', '5', 'A'])
        from npcryption import encrypt as core_enc
        assert cli.encrypt(17, 19, 5, 'Hello') == core_enc(17, 19, 5, 'Hello')


# ---------------------------------------------------------------------------
# Tests for cli.decrypt wrapper
# ---------------------------------------------------------------------------

class TestCliDecryptWrapper:
    """cli.decrypt() is a thin wrapper around Decryption.decrypt."""

    def test_returns_string(self):
        cli = _load_cli(['D', '17', '19', '5', '021'])
        result = cli.decrypt(17, 19, 5, '021')
        assert isinstance(result, str)

    def test_known_value(self):
        cli = _load_cli(['D', '17', '19', '5', '021'])
        assert cli.decrypt(17, 19, 5, '021') == 'H'

    def test_empty_message(self):
        cli = _load_cli(['D', '17', '19', '5', ''])
        assert cli.decrypt(17, 19, 5, '') == ''

    def test_round_trip(self):
        cli = _load_cli(['E', '17', '19', '5', 'Hello'])
        cipher = cli.encrypt(17, 19, 5, 'Hello')
        assert cli.decrypt(17, 19, 5, cipher) == 'Hello'

    def test_delegates_to_core(self):
        cli = _load_cli(['D', '17', '19', '5', '021'])
        from npcryption import decrypt as core_dec
        assert cli.decrypt(17, 19, 5, '021') == core_dec(17, 19, 5, '021')


# ---------------------------------------------------------------------------
# Tests for cli.main()
# ---------------------------------------------------------------------------

class TestCliMain:
    """Tests for the interactive main() function."""

    def test_main_encrypt_prints_result(self, capsys):
        """Choosing 'E' should print the encrypted ciphertext."""
        cli = _load_cli(['E', '17', '19', '5', 'H'])

        with patch('builtins.input', side_effect=['E', '17', '19', '5', 'H']):
            cli.main()

        captured = capsys.readouterr()
        assert '021' in captured.out

    def test_main_decrypt_prints_result(self, capsys):
        """Choosing 'D' should print the decrypted plaintext."""
        cli = _load_cli(['D', '17', '19', '5', '021'])

        with patch('builtins.input', side_effect=['D', '17', '19', '5', '021']):
            cli.main()

        captured = capsys.readouterr()
        assert 'H' in captured.out

    def test_main_lowercase_e_accepted(self, capsys):
        """Lowercase 'e' should also trigger encryption."""
        cli = _load_cli(['e', '17', '19', '5', 'A'])

        with patch('builtins.input', side_effect=['e', '17', '19', '5', 'A']):
            cli.main()

        captured = capsys.readouterr()
        assert '012' in captured.out

    def test_main_lowercase_d_accepted(self, capsys):
        """Lowercase 'd' should also trigger decryption."""
        cli = _load_cli(['d', '17', '19', '5', '012'])

        with patch('builtins.input', side_effect=['d', '17', '19', '5', '012']):
            cli.main()

        captured = capsys.readouterr()
        assert 'A' in captured.out

    def test_main_unknown_choice_produces_no_output(self, capsys):
        """An unrecognised choice ('X') should produce no encrypt/decrypt output."""
        cli = _load_cli(['X', '17', '19', '5'])

        with patch('builtins.input', side_effect=['X', '17', '19', '5']):
            cli.main()

        captured = capsys.readouterr()
        # Neither an encryption block nor a plaintext character is printed
        assert captured.out == ''

    def test_main_encrypt_long_message(self, capsys):
        """Encryption of a longer message should produce the full ciphertext."""
        msg = 'Hi'
        from npcryption import encrypt as core_enc
        expected = core_enc(17, 19, 5, msg)

        cli = _load_cli(['E', '17', '19', '5', msg])
        with patch('builtins.input', side_effect=['E', '17', '19', '5', msg]):
            cli.main()

        captured = capsys.readouterr()
        assert expected in captured.out

