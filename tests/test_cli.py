"""
Tests for npcryption.cli module.

Covers:
  - importing the module (no interactive side effects)
  - encrypt() / decrypt() wrappers
  - main() prompts and output, with builtins.input patched
  - running the module as a script (`python -m npcryption.cli`)
"""
import os
import subprocess
import sys
from unittest.mock import patch

import npcryption.cli as cli
from npcryption import encrypt as core_enc, decrypt as core_dec

_SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))


def _run_main(inputs):
    """Run cli.main() with builtins.input returning *inputs* in order."""
    with patch('builtins.input', side_effect=inputs):
        cli.main()


# ---------------------------------------------------------------------------
# Tests for importing the module
# ---------------------------------------------------------------------------

class TestCliImport:
    """Importing npcryption.cli must not start the interactive session."""

    def test_import_does_not_prompt(self):
        sys.modules.pop('npcryption.cli', None)
        with patch('builtins.input') as mock_input:
            import npcryption.cli  # noqa: F401
        mock_input.assert_not_called()

    def test_main_is_callable(self):
        assert callable(cli.main)


# ---------------------------------------------------------------------------
# Tests for cli.encrypt wrapper
# ---------------------------------------------------------------------------

class TestCliEncryptWrapper:
    """cli.encrypt() is a thin wrapper around Encryption.encrypt."""

    def test_returns_string(self):
        result = cli.encrypt(17, 19, 5, 'A')
        assert isinstance(result, str)

    def test_known_value(self):
        assert cli.encrypt(17, 19, 5, 'H') == '021'

    def test_empty_message(self):
        assert cli.encrypt(17, 19, 5, '') == ''

    def test_delegates_to_core(self):
        assert cli.encrypt(17, 19, 5, 'Hello') == core_enc(17, 19, 5, 'Hello')


# ---------------------------------------------------------------------------
# Tests for cli.decrypt wrapper
# ---------------------------------------------------------------------------

class TestCliDecryptWrapper:
    """cli.decrypt() is a thin wrapper around Decryption.decrypt."""

    def test_returns_string(self):
        result = cli.decrypt(17, 19, 5, '021')
        assert isinstance(result, str)

    def test_known_value(self):
        assert cli.decrypt(17, 19, 5, '021') == 'H'

    def test_empty_message(self):
        assert cli.decrypt(17, 19, 5, '') == ''

    def test_round_trip(self):
        cipher = cli.encrypt(17, 19, 5, 'Hello')
        assert cli.decrypt(17, 19, 5, cipher) == 'Hello'

    def test_delegates_to_core(self):
        assert cli.decrypt(17, 19, 5, '021') == core_dec(17, 19, 5, '021')


# ---------------------------------------------------------------------------
# Tests for cli.main()
# ---------------------------------------------------------------------------

class TestCliMain:
    """Tests for the interactive main() function."""

    def test_main_encrypt_prints_result(self, capsys):
        """Choosing 'E' should print the encrypted ciphertext."""
        _run_main(['E', '17', '19', '5', 'H'])
        assert capsys.readouterr().out == '021\n'

    def test_main_decrypt_prints_result(self, capsys):
        """Choosing 'D' should print the decrypted plaintext."""
        _run_main(['D', '17', '19', '5', '021'])
        assert capsys.readouterr().out == 'H\n'

    def test_main_lowercase_e_accepted(self, capsys):
        """Lowercase 'e' should also trigger encryption."""
        _run_main(['e', '17', '19', '5', 'A'])
        assert capsys.readouterr().out == '012\n'

    def test_main_lowercase_d_accepted(self, capsys):
        """Lowercase 'd' should also trigger decryption."""
        _run_main(['d', '17', '19', '5', '012'])
        assert capsys.readouterr().out == 'A\n'

    def test_main_unknown_choice_produces_no_output(self, capsys):
        """An unrecognised choice ('X') should produce no encrypt/decrypt output."""
        _run_main(['X', '17', '19', '5'])
        assert capsys.readouterr().out == ''

    def test_main_encrypt_long_message(self, capsys):
        """Encryption of a longer message should produce the full ciphertext."""
        msg = 'Hello'
        _run_main(['E', '17', '19', '5', msg])
        assert capsys.readouterr().out == core_enc(17, 19, 5, msg) + '\n'

    def test_main_prompts_in_order(self):
        """main() asks for the choice, P, Q, E and then the message."""
        with patch('builtins.input', side_effect=['E', '17', '19', '5', 'H']) as mock_input:
            cli.main()
        prompts = [call.args[0] for call in mock_input.call_args_list]
        assert prompts == [
            'Press E for Encryption or D for Decryption: ',
            'Enter Private Key P: ',
            'Enter Private Key Q: ',
            'Enter Public Key E: ',
            'Enter Message: ',
        ]


# ---------------------------------------------------------------------------
# Tests for running the module as a script
# ---------------------------------------------------------------------------

class TestCliAsScript:
    """`python -m npcryption.cli` must start the interactive session."""

    def _run(self, stdin):
        env = dict(os.environ)
        env['PYTHONPATH'] = os.pathsep.join(filter(None, [_SRC_DIR, env.get('PYTHONPATH')]))
        return subprocess.run(
            [sys.executable, '-m', 'npcryption.cli'],
            input=stdin, capture_output=True, text=True, env=env, timeout=30,
        )

    def test_encrypt(self):
        result = self._run('E\n17\n19\n5\nHello\n')
        assert result.returncode == 0, result.stderr
        assert result.stdout.endswith('021271109109042\n')

    def test_decrypt(self):
        result = self._run('D\n17\n19\n5\n021271109109042\n')
        assert result.returncode == 0, result.stderr
        assert result.stdout.endswith('Hello\n')
