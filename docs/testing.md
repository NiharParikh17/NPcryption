# Testing

---

## Test Framework

NPcryption uses **pytest**. The test suite lives under `tests/`.

### pytest configuration (`setup.cfg`)

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

`tests/conftest.py` inserts `src/` at the front of `sys.path`, so the suite runs from a fresh clone even without `pip install -e .`.

---

## Running Tests

```bash
pip install pytest

# From the project root
pytest
```

Run with verbose output:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest tests/test_encryption.py
```

---

## Test Suite Layout

| File | Covers |
|---|---|
| `test_package.py` | `npcryption.__version__`, `__all__`, and the re-exported `encrypt` / `decrypt` |
| `test_encryption.py` | `getAscii`, `getCharacter`, `encryptCharacter`, `encrypt` (known values, padding, caching) |
| `test_decryption.py` | `getAscii`, `getCharacter`, `decryptCharacter`, `decrypt` (block parsing, caching) |
| `test_encryption_table.py` | `split_into_valid_powers_of_2`, `get_highest_power_of_2`, `EncryptionTable` init, length and setters |
| `test_decryption_table.py` | `DecryptionTable` inheritance, derived `D`, and `getD` |
| `test_dtable.py` | `DTable` initial state, `generateTable()` and `getD()` |
| `test_cli.py` | Side-effect-free import, `cli.encrypt` / `cli.decrypt` wrappers, `cli.main()` prompts and output, and `python -m npcryption.cli` |
| `test_integration.py` | End-to-end `encrypt` → `decrypt` round-trips across several key sets, including every printable ASCII character |

The reference key sets used throughout are:

| P | Q | E | N | φ(N) | D |
|---|---|---|---|---|---|
| 17 | 19 | 5 | 323 | 288 | 173 |
| 61 | 53 | 17 | 3233 | 3120 | 2753 |
| 11 | 13 | 7 | 143 | 120 | 103 |

`test_integration.py` also uses two small-N key sets (`N = 91` and `N = 55`) with messages restricted to characters whose code point is below N. One parametrised case is **expected to be skipped** (`N=55 too small for 'A'`).

### How `test_cli.py` tests the CLI

- `cli.main()` is called with `builtins.input` patched to feed the answers, and `capsys` captures what it prints.
- `TestCliImport` checks that importing `npcryption.cli` never calls `input()`.
- `TestCliAsScript` runs `python -m npcryption.cli` in a subprocess (with `src/` on `PYTHONPATH`) to cover the real launch path end to end.

---

## Writing Tests

Place test files in the `tests/` directory following the naming convention `test_*.py`. Test functions must start with `test_`, and test classes with `Test`.

Pick keys where `N = P × Q` is larger than every character code in the message; otherwise the round-trip fails by design (see [Choosing N large enough](algorithm.md#choosing-n-large-enough)).

### Example: encryption round-trip test

```python
from npcryption import encrypt, decrypt

def test_encrypt_decrypt_roundtrip():
    P, Q, E = 61, 53, 17
    message = "Hello, World!"
    assert decrypt(P, Q, E, encrypt(P, Q, E, message)) == message

def test_known_ciphertext():
    assert encrypt(17, 19, 5, "H") == "021"
    assert decrypt(17, 19, 5, "021") == "H"

def test_empty_string():
    P, Q, E = 61, 53, 17
    assert encrypt(P, Q, E, "") == ""
    assert decrypt(P, Q, E, "") == ""
```

### Example: EncryptionTable unit test

```python
from npcryption.core.EncryptionTable import (
    EncryptionTable,
    get_highest_power_of_2,
    split_into_valid_powers_of_2,
)

def test_split_powers_of_2():
    assert split_into_valid_powers_of_2(7) == [1, 2, 4]
    assert split_into_valid_powers_of_2(6) == [2, 4]

def test_highest_power_of_2():
    assert get_highest_power_of_2(7) == 4
    assert get_highest_power_of_2(8) == 8

def test_table_length():
    t = EncryptionTable(5)   # 5 = (101)₂ → rows for powers 1, 2, 4
    assert t.get_length() == 3
    assert t.validity == [True, False, True]
```

### Example: DTable unit test

```python
from npcryption.core.DTable import DTable

def test_get_d_basic():
    dt = DTable(288, 5)      # φ(N) for P=17, Q=19
    dt.generateTable()
    assert dt.getD(288) == 173

def test_d_times_e_is_1_mod_phi():
    P, Q, E = 61, 53, 17
    phi = (P - 1) * (Q - 1)
    dt = DTable(phi, E)
    dt.generateTable()
    assert (E * dt.getD(phi)) % phi == 1
```

---

## Linting

```bash
pip install flake8
flake8 src/ tests/
```

Configured in `setup.cfg` with a max line length of 100. The codebase is currently flake8-clean and CI fails on any new warning.

---

## Continuous Integration

GitHub Actions workflows live in `.github/workflows/`.

### `ci.yml` — runs on every push to `main`, every pull request, and on demand

| Job | What it does |
|---|---|
| **Lint** | `flake8 src/ tests/` on Python 3.12 |
| **Test** | `pip install -e . pytest` then `pytest -v` on Python 3.10, 3.11 and 3.12 |
| **Build distribution** | Runs after Lint and Test pass: `python -m build`, `twine check --strict dist/*`, installs the wheel, performs a round-trip smoke test and pipes a sample session through the `npcryption` command, then uploads `dist/` as the `dist` artifact |

To reproduce CI locally:

```bash
pip install -e . pytest flake8 build twine
flake8 src/ tests/
pytest -v
python -m build
twine check --strict dist/*
```

### `release.yml` — creates the tag and GitHub release

Runs when:

- a push to `main` changes `pyproject.toml` or `src/npcryption/__init__.py` (for example, merging a version bump),
- it is started manually on `main` from **Actions → Release → Run workflow**, or
- a `v*` tag is pushed by hand.

Steps:

1. **Check version** — reads the version from `pyproject.toml`, fails if `npcryption.__version__` differs, and works out the tag `v<version>`. For a pushed tag, the tag must match. On `main`, nothing more happens if that tag or release already exists. Manual runs on any other branch fail.
2. Runs the full `ci.yml` workflow.
3. Builds the sdist and wheel and runs `twine check`.
4. Creates the tag on the tested commit (unless it already exists) and a GitHub release with auto-generated notes and the built files attached.

The release workflow does not publish to PyPI.

### Cutting a release

1. In a pull request, update `version` in `pyproject.toml` and `__version__` in `src/npcryption/__init__.py` (and `test_version_value` in `tests/test_package.py`).
2. Merge it to `main`. The release workflow tags `v<version>` and publishes the release automatically.

If the automatic run did not happen or failed, re-run it from the Actions tab or start it manually on `main`.
