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

---

## Running Tests

```bash
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

## Writing Tests

Place test files in the `tests/` directory following the naming convention `test_*.py`. Test functions must start with `test_`.

### Example: encryption round-trip test

```python
# tests/test_roundtrip.py

from npcryption import encrypt, decrypt

def test_encrypt_decrypt_roundtrip():
    P, Q, E = 61, 53, 17
    message = "Hello, World!"
    assert decrypt(P, Q, E, encrypt(P, Q, E, message)) == message

def test_single_character():
    P, Q, E = 3, 11, 7
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz":
        assert decrypt(P, Q, E, encrypt(P, Q, E, ch)) == ch

def test_empty_string():
    P, Q, E = 61, 53, 17
    assert encrypt(P, Q, E, "") == ""
    assert decrypt(P, Q, E, "") == ""

def test_repeated_characters():
    P, Q, E = 61, 53, 17
    message = "aaaaaa"
    assert decrypt(P, Q, E, encrypt(P, Q, E, message)) == message
```

### Example: EncryptionTable unit test

```python
# tests/test_encryption_table.py

from npcryption.core.EncryptionTable import EncryptionTable, splitIntoValidPowersOf2, getHighestPowerOf2

def test_split_powers_of_2():
    assert splitIntoValidPowersOf2(7) == [1, 2, 4]
    assert splitIntoValidPowersOf2(6) == [2, 4]
    assert splitIntoValidPowersOf2(4) == [4]
    assert splitIntoValidPowersOf2(1) == [1]

def test_highest_power_of_2():
    assert getHighestPowerOf2(7) == 4
    assert getHighestPowerOf2(8) == 8
    assert getHighestPowerOf2(9) == 8

def test_table_length():
    t = EncryptionTable(7)   # 7 = (111)₂  → 3 rows
    assert t.getLength() == 3
    t2 = EncryptionTable(4)  # 4 = (100)₂  → 1 or 3 rows depending on start
    assert t2.getLength() >= 1
```

### Example: DTable unit test

```python
# tests/test_dtable.py

from npcryption.core.DTable import DTable

def test_get_d_basic():
    # E=7, phi=20  →  D=3  (7*3 = 21 ≡ 1 mod 20)
    dt = DTable(20, 7)
    dt.generateTable()
    assert dt.getD(20) == 3

def test_d_times_e_is_1_mod_phi():
    P, Q, E = 61, 53, 17
    phi = (P - 1) * (Q - 1)
    dt = DTable(phi, E)
    dt.generateTable()
    D = dt.getD(phi)
    assert (E * D) % phi == 1
```

---

## Linting

```bash
flake8 src/ tests/
```

Configured with max line length 100.

---

## Continuous Integration

No CI pipeline is configured in v0.1.0. A GitHub Actions workflow is recommended for future versions:

```yaml
# .github/workflows/test.yml (example)
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e . pytest
      - run: pytest -v
```

