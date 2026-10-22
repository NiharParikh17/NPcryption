# Installation & Setup

---

## Prerequisites

| Requirement | Minimum version |
|---|---|
| Python | 3.10 |
| pip | 21+ (supports PEP 517 builds) |

No third-party runtime packages are required.

---

## Install from GitHub

NPcryption is not published on PyPI. Install the latest code from `main`:

```bash
pip install "git+https://github.com/NiharParikh17/NPcryption.git"
```

or pin a release tag:

```bash
pip install "git+https://github.com/NiharParikh17/NPcryption.git@v0.1.0"
```

Each [GitHub release](https://github.com/NiharParikh17/NPcryption/releases) also has a wheel (`.whl`) attached, which can be installed directly with `pip install <wheel URL or file>`.

---

## Install from Source (Development Mode)

Clone the repository and install in editable mode:

```bash
git clone https://github.com/NiharParikh17/NPcryption.git
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

This invokes `npcryption.cli:main` as registered in `pyproject.toml`. `python -m npcryption.cli` does the same. See the [CLI Guide](cli.md) for a walkthrough.

---

## Use as a Library

```python
from npcryption import encrypt, decrypt

# Choose primes P, Q and a public exponent E coprime with (P-1)*(Q-1).
# N = P*Q must be larger than every character code in the message.
P, Q, E = 61, 53, 17

ciphertext = encrypt(P, Q, E, "Hello, World!")
print(ciphertext)  # → 3000131307450745218506781992060421852412074517731853

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

To reproduce the CI packaging checks locally, also install `build` and `twine`:

```bash
pip install build twine
python -m build
twine check --strict dist/*
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
| `.github/workflows/ci.yml` | CI: lint, test matrix and package build |
| `.github/workflows/release.yml` | Release: tags new versions and publishes a GitHub release |
| `.github/workflows/pages.yml` | Website: publishes `web/` to GitHub Pages |

