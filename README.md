# NPcryption

Encrypts and Decrypts user input using RSA cryptography.

## Project Structure

```
NPcryption/
├── src/
│   └── npcryption/          # Installable Python package
│       ├── __init__.py      # Public API (encrypt / decrypt)
│       ├── cli.py           # Interactive command-line entry point
│       └── core/            # Core cryptographic primitives
│           ├── __init__.py
│           ├── Encryption.py
│           ├── Decryption.py
│           ├── EncryptionTable.py
│           ├── DecryptionTable.py
│           └── DTable.py
├── tests/                   # Test suite
│   └── __init__.py
├── docs/                    # Documentation
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── README.md
├── pyproject.toml           # Build & project metadata
└── setup.cfg                # Tool configuration (pytest, flake8)
```

## Installation

```bash
pip install -e .
```

## Usage

### CLI

```bash
npcryption
```

### Library

```python
from npcryption import encrypt, decrypt

ciphertext = encrypt(P, Q, E, "Hello")
plaintext  = decrypt(P, Q, E, ciphertext)
```

## Algorithm

NPcryption implements RSA encryption using the square-and-multiply method for
fast modular exponentiation. The private exponent `D` is derived via the
Extended Euclidean Algorithm (`DTable`).

## License

See [LICENSE](LICENSE).
