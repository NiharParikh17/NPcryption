# Tech Stack

This document describes every language, runtime, framework, and tooling decision used in NPcryption.

---

## Language

| Item | Detail |
|---|---|
| **Language** | Python |
| **Minimum version** | Python 3.10 |
| **Tested on** | Python 3.10, 3.11, 3.12 (CI matrix) |

Python was chosen for its readability and its suitability for expressing mathematical algorithms concisely. No external runtime is required.

---

## Standard Library Usage

NPcryption uses only the Python **standard library** — there are **zero third-party runtime dependencies**.

| Module | Where used | Purpose |
|---|---|---|
| `math` | `EncryptionTable.py` | `math.log` to find the highest power of 2 ≤ n |
| `builtins.ord` | `Encryption.py`, `Decryption.py` | Convert a character to its ASCII integer value |
| `builtins.chr` | `Encryption.py`, `Decryption.py` | Convert an ASCII integer back to a character |

---

## Build System

| Tool | Version constraint | Role |
|---|---|---|
| **setuptools** | ≥ 68 | Package building and metadata |
| **wheel** | latest | Binary distribution format |
| **pyproject.toml** | PEP 517/518 | Single source of truth for project metadata and build config |
| **setup.cfg** | — | Tool configuration (pytest, flake8) |

### `pyproject.toml` highlights

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "npcryption"
version = "0.1.0"
license = { file = "LICENSE" }
requires-python = ">=3.10"
keywords = ["rsa", "cryptography", "encryption", "decryption"]
```

> **Note:** Current setuptools releases warn that the `license = { file = ... }` table form and the `License ::` classifier are deprecated in favour of an SPDX string (`license = "MIT"`), with support ending on 2027-02-18. The build still succeeds today.

The package version is declared in two places, `pyproject.toml` and `src/npcryption/__init__.py`. The release workflow fails if they differ from the pushed tag.

---

## Package Layout (src layout)

NPcryption uses the modern **src layout** recommended by the Python Packaging Authority (PyPA):

```
src/
└── npcryption/        ← installable package root
    ├── __init__.py
    ├── cli.py
    └── core/
```

This means the package is only importable when properly installed (e.g. `pip install -e .`), preventing accidental imports from the repository root. The one exception is the test suite: `tests/conftest.py` adds `src/` to `sys.path` so `pytest` also works without an install.

---

## Entry Points / CLI

Defined in `pyproject.toml`:

```toml
[project.scripts]
npcryption = "npcryption.cli:main"
```

After installation, running `npcryption` in any terminal calls `cli.main()`. In v0.1.0 this fails at import time; see the [CLI Guide](cli.md#known-issue-in-v010).

---

## Development & Quality Tools

| Tool | Config location | Purpose |
|---|---|---|
| **pytest** | `setup.cfg` → `[tool:pytest]` | Test runner |
| **flake8** | `setup.cfg` → `[flake8]` | PEP 8 style linting, max line length 100 |
| **build** | — | Builds the sdist and wheel (`python -m build`) |
| **twine** | — | Validates distribution metadata (`twine check --strict`) |
| **GitHub Actions** | `.github/workflows/` | CI (lint, tests, build) and tag-driven releases |

### pytest configuration

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### flake8 configuration

```ini
[flake8]
max-line-length = 100
exclude = .git, __pycache__, .venv, venv, build, dist
```

---

## License

**MIT License** — permissive open-source license. See `LICENSE` for the full text.

---

## Classifiers (PyPI)

```
Development Status :: 3 - Alpha
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python :: 3
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3.11
Programming Language :: Python :: 3.12
Topic :: Security :: Cryptography
```

