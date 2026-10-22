# NPcryption

[![CI](https://github.com/NiharParikh17/NPcryption/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/NiharParikh17/NPcryption/actions/workflows/ci.yml)

Encrypts and Decrypts user input using RSA cryptography.

NPcryption is an educational, pure-Python implementation of RSA with no
third-party runtime dependencies. It is **not** intended to protect real data.

**Try it in your browser:** <https://niharparikh17.github.io/NPcryption/> is an interactive demo
that runs this library (via Pyodide) and shows every step of key setup, encryption and decryption.

## Project Structure

```
NPcryption/
├── .github/
│   ├── ISSUE_TEMPLATE/      # Bug report and feature request forms
│   ├── dependabot.yml       # Monthly GitHub Actions version updates
│   └── workflows/
│       ├── ci.yml           # Lint, test matrix and package build
│       ├── pages.yml        # Publishes web/ to GitHub Pages
│       └── release.yml      # Tags and publishes a GitHub release
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
├── tests/                   # pytest suite (unit + integration)
├── docs/                    # Documentation
├── web/                     # Interactive demo website (GitHub Pages)
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml           # Build & project metadata
└── setup.cfg                # Tool configuration (pytest, flake8)
```

## Installation

Requires Python 3.10 or newer. NPcryption is not on PyPI; install it from GitHub:

```bash
pip install "git+https://github.com/NiharParikh17/NPcryption.git"
```

Add `@v0.1.0` (or any tag from [Releases](https://github.com/NiharParikh17/NPcryption/releases))
to the URL to pin a release; each release also has a wheel you can install directly. See
[Installation & Setup](docs/installation.md) for details.

## Usage

### Library

```python
from npcryption import encrypt, decrypt

P, Q, E = 17, 19, 5                   # N = 323, φ(N) = 288

ciphertext = encrypt(P, Q, E, "Hello")  # "021271109109042"
plaintext  = decrypt(P, Q, E, ciphertext)  # "Hello"
```

Key requirements (none of them are validated by the library):

- `P` and `Q` are distinct primes.
- `E` is coprime with `(P-1) * (Q-1)`.
- `N = P * Q` is larger than the code point of every character in the
  message (at least 127 for printable ASCII).

### CLI

```bash
npcryption              # or: python -m npcryption.cli
```

The CLI prompts for the operation (E/D), the keys `P`, `Q`, `E` and the
message, then prints the result. See the [CLI Guide](docs/cli.md).

## Algorithm

NPcryption implements RSA encryption using the square-and-multiply method for
fast modular exponentiation. The private exponent `D` is derived via the
Extended Euclidean Algorithm (`DTable`).

## Development

```bash
pip install -e . pytest flake8
pytest -v
flake8 src/ tests/
```

Every push to `main` and every pull request runs the
[CI workflow](.github/workflows/ci.yml): flake8, pytest on Python 3.10–3.14,
and a package build check. When a new version in `pyproject.toml` reaches
`main`, the [release workflow](.github/workflows/release.yml) creates the
`v<version>` tag and publishes a GitHub release with the built sdist and
wheel; it can also be run manually. See [Testing](docs/testing.md#cutting-a-release)
for details.

## Documentation

Full documentation lives in [`docs/`](docs/index.md): overview, architecture,
algorithm walkthrough, API reference, CLI guide, installation, testing and
contributing.

## Contributing

Contributions are welcome. The [contributing guide](docs/contributing.md) covers setup,
code style and the pull request process; for larger changes, please open an issue first.

## Reporting issues

Found a bug or have an idea? [Open an issue](https://github.com/NiharParikh17/NPcryption/issues/new/choose)
and pick **Bug report** or **Feature request**.

## License

See [LICENSE](LICENSE).
