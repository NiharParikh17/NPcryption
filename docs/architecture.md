# Architecture

This document describes the project's directory structure and explains how the modules relate to one another.

---

## Directory Structure

```
NPcryption/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Lint, test matrix (3.10–3.12) and package build
│       └── release.yml            # Builds and publishes a GitHub release on v* tags
├── src/
│   └── npcryption/                # Installable Python package
│       ├── __init__.py            # Public API — re-exports encrypt() and decrypt()
│       ├── cli.py                 # Interactive command-line entry point
│       └── core/                  # Core cryptographic primitives
│           ├── __init__.py        # Package docstring listing all sub-modules
│           ├── Encryption.py      # RSA encryption logic (character-level)
│           ├── Decryption.py      # RSA decryption logic (character-level)
│           ├── EncryptionTable.py # Square-and-multiply table (shared by enc + dec)
│           ├── DecryptionTable.py # Derives private exponent D; wraps EncryptionTable
│           └── DTable.py          # Extended Euclidean Algorithm implementation
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Puts src/ on sys.path for un-installed runs
│   ├── test_package.py            # Public API, __version__, __all__
│   ├── test_encryption.py         # Encryption module
│   ├── test_decryption.py         # Decryption module
│   ├── test_encryption_table.py   # EncryptionTable and helper functions
│   ├── test_decryption_table.py   # DecryptionTable
│   ├── test_dtable.py             # DTable (Extended Euclidean Algorithm)
│   ├── test_cli.py                # cli wrappers and main()
│   └── test_integration.py        # encrypt ↔ decrypt round-trips
├── docs/                          # This documentation
├── LICENSE                        # MIT License
├── README.md                      # Quick-start readme
├── pyproject.toml                 # Build metadata and entry points
└── setup.cfg                      # pytest and flake8 configuration
```

---

## Module Dependency Graph

```
cli.py
 ├── Encryption.py
 └── Decryption.py

npcryption/__init__.py
 ├── Encryption.py   ← encrypt()
 └── Decryption.py   ← decrypt()

Encryption.py
 └── EncryptionTable.py
         └── (math stdlib)

Decryption.py
 └── DecryptionTable.py
         ├── EncryptionTable.py   (inheritance)
         └── DTable.py
```

---

## Module Responsibilities

### `npcryption/__init__.py`
The public surface of the package. It imports `encrypt` from `Encryption.py` and `decrypt` from `Decryption.py` and re-exports them via `__all__`. The package version is declared here as `__version__ = "0.1.0"`.

### `npcryption/cli.py`
An interactive command-line script. It:
1. Prompts the user to choose encryption (`E`) or decryption (`D`).
2. Collects the RSA key parameters P, Q, and E from standard input.
3. Accepts the plaintext or ciphertext from standard input.
4. Calls `encrypt()` or `decrypt()` and prints the result.

> **Note:** `cli.py` currently imports `Encryption` and `Decryption` directly (without the `npcryption.core` prefix). Those names do not resolve in any normal launch — the installed `npcryption` entry point, `python -m npcryption.cli`, and `python src/npcryption/cli.py` all fail with `ModuleNotFoundError: No module named 'Encryption'`. `cli.py` also calls `main()` at module level. See the [CLI Guide](cli.md#known-issue-in-v010) for a workaround; `tests/test_cli.py` uses the same technique.

### `core/Encryption.py`
Implements the full string-level RSA encryption routine. Iterates over each character of the plaintext, converts it to its ASCII code, applies modular exponentiation (`M^E mod N`), and zero-pads the result to a fixed block width equal to `len(str(N))`. A cache dictionary (`encyptedDict`) avoids recomputing the same character twice.

### `core/Decryption.py`
Implements the full string-level RSA decryption routine. Splits the ciphertext string back into fixed-width numeric blocks, converts each block to an integer, and applies modular exponentiation (`C^D mod N`), recovering the original ASCII value and thus the original character. A cache dictionary (`decryptDict`) avoids recomputing.

### `core/EncryptionTable.py`
The computational engine for **modular exponentiation by squaring** (also known as the square-and-multiply method). Given an exponent `n`, it:
1. Decomposes `n` into its constituent powers of 2 using `split_into_valid_powers_of_2`.
2. Stores successive squarings and their mod results per row.
3. Exposes `get_product()` which multiplies only the rows whose power-of-2 is present in the binary representation of `n`.

Shared by both encryption (exponent = E) and decryption (exponent = D).

### `core/DecryptionTable.py`
A thin subclass of `EncryptionTable`. Its constructor:
1. Calls `DTable` to compute the private exponent `D` from φ(N) = (P−1)(Q−1) and `E`.
2. Passes `D` to `EncryptionTable.__init__`, so the same square-and-multiply machinery is used for decryption.

### `core/DTable.py`
Implements the **Extended Euclidean Algorithm** to find the modular inverse of `E` modulo φ(N). This produces the private exponent `D` satisfying `E × D ≡ 1 (mod φ(N))`. The algorithm is run iteratively, tracking columns R (remainders), X, D, and Q (quotients) until the remainder reaches 1 or 0.

---

## Data Flow: Encryption

```
plaintext string
      │
      ▼
  EncryptionTable(E)         ← built once, reused for every character
      │
      ▼ (for each char not already in the cache)
  encryptCharacter(PQ, char, table)
      ├── M = ord(char)
      ├── table.set_prev_sqr(M, 0)
      ├── modNum = M % PQ
      ├── table.set_mod_num(modNum, 0)
      ├── loop: square & mod for each row
      └── table.get_product() % PQ  → C (cipher integer)
      │
      ▼
  zero-pad C to len(str(PQ)) digits
      │
      ▼
  concatenate → ciphertext string
```

## Data Flow: Decryption

```
ciphertext string
      │
      ▼
  DecryptionTable((P-1)*(Q-1), E)  ← built once, reused for every block
      ├── DTable.generateTable()   ← Extended Euclidean
      └── DTable.getD(φN)          → private exponent D
      │
      ▼ (slice blocks of len(str(PQ)) digits)
  int(block) → cipher integer C
      │
      ▼ (for each C not already in the cache; table uses exponent D)
  decryptCharacter(PQ, C, table)
      ├── table.set_prev_sqr(C, 0)
      ├── table.set_mod_num(C % PQ, 0)
      ├── loop: square & mod
      └── table.get_product() % PQ  → M (ASCII int)
      │
      ▼
  chr(M) → character
      │
      ▼
  concatenate → plaintext string
```

