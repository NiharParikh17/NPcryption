# Contributing

Thank you for your interest in contributing to NPcryption!

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/NPcryption.git
   cd NPcryption
   ```
3. Create a **virtual environment** and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   pip install pytest flake8
   ```
4. Create a **feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Code Style

- Follow **PEP 8**.
- Maximum line length: **100 characters** (enforced by flake8).
- Use descriptive variable names consistent with the existing style (e.g. `PQ`, `prevSQR`, `modNum`).
- Add docstrings to all public functions and classes.

Run the linter before committing:

```bash
flake8 src/ tests/
```

---

## Project Conventions

| Convention | Detail |
|---|---|
| **src layout** | All package code lives under `src/npcryption/` |
| **File naming** | Core module files use PascalCase (e.g. `EncryptionTable.py`) |
| **Test naming** | Test files: `test_*.py`; test functions: `test_*` |
| **No external deps** | Runtime code must use only the Python standard library |

---

## Submitting Changes

1. Make sure all existing and new tests pass:
   ```bash
   pytest -v
   ```
2. Make sure flake8 reports no errors:
   ```bash
   flake8 src/ tests/
   ```
3. **Commit** with a clear message:
   ```bash
   git commit -m "feat: add padding validation for encrypt()"
   ```
4. **Push** and open a **Pull Request** against the `main` branch.

---

## Areas for Contribution

- **Tests** — The `tests/` directory is currently empty. Writing comprehensive unit and integration tests is the highest-priority contribution.
- **CLI improvements** — Accept command-line arguments (e.g. argparse), support file I/O.
- **Padding scheme** — Implement PKCS#1 v1.5 or OAEP padding for educational parity with real-world RSA.
- **Key validation** — Validate that P and Q are prime and that E is coprime with φ(N) at call time.
- **CI/CD** — Add a GitHub Actions workflow (see [Testing](testing.md)).
- **Documentation** — Improve or expand any doc page.

---

## Reporting Issues

Open a GitHub Issue and include:
- Python version (`python --version`)
- Operating system
- Steps to reproduce
- Expected vs. actual behaviour

