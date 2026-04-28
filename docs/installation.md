# Installation & Setup

---

## Prerequisites

| Requirement | Minimum version |
|---|---|
| Python | 3.10 |
| pip | 21+ (supports PEP 517 builds) |

No third-party runtime packages are required.

---

## Install from Source (Development Mode)

Clone the repository and install in editable mode:

```bash
git clone <repository-url>
cd NPcryption
pip install -e .
```

The `-e` flag installs the package in **editable** mode, meaning changes to source files under `src/` are immediately reflected without reinstalling.

---

## Verify Installation

```bash
python -c "import npcryption; print(npcryption.__version__)"
# 0.1.0
```

---

## Run the CLI

```bash
npcryption
```

This invokes `npcryption.cli:main` as registered in `pyproject.toml`.

---

## Use as a Library

```python
from npcryption import encrypt, decrypt

# Choose primes P, Q and a public exponent E coprime with (P-1)*(Q-1)
P, Q, E = 61, 53, 17

ciphertext = encrypt(P, Q, E, "Hello, World!")
print(ciphertext)

plaintext = decrypt(P, Q, E, ciphertext)
print(plaintext)   # → Hello, World!
```

---

## Build a Distribution

```bash
pip install build
python -m build
```

Produces `dist/npcryption-0.1.0.tar.gz` and `dist/npcryption-0.1.0-py3-none-any.whl`.

---

## Install Development Dependencies

For running tests and linting, install optional tools:

```bash
pip install pytest flake8
```

---

## Virtual Environment (Recommended)

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows

pip install -e .
pip install pytest flake8
```

---

## Project Configuration Files

| File | Purpose |
|---|---|
| `pyproject.toml` | Build system configuration, project metadata, entry points |
| `setup.cfg` | pytest and flake8 tool configuration |

