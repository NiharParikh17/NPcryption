# Overview

## What is NPcryption?

**NPcryption** is a pure-Python library and command-line tool that implements **RSA (Rivest–Shamir–Adleman) public-key cryptography** to encrypt and decrypt text messages.

It is designed as an educational implementation of RSA that exposes the underlying mathematical machinery — prime key selection, modular exponentiation via the square-and-multiply method, and private-key derivation via the Extended Euclidean Algorithm — without relying on any external cryptographic library.

---

## Goals

- Provide a clean, readable implementation of RSA useful for learning cryptography.
- Expose a simple Python API (`encrypt` / `decrypt`) that can be imported into other projects.
- Offer an interactive CLI for quick encryption/decryption without writing code.

---

## What It Is NOT

- **Not production-safe cryptography.** NPcryption is an educational implementation. It does not use cryptographically secure random number generation, padding schemes (e.g. OAEP), or side-channel protections. Do **not** use it to protect sensitive real-world data.
- **Not an asymmetric-key exchange system.** Both parties must know P, Q, and E. Key distribution is left entirely to the user.
- **Not a block cipher.** Each character is encrypted on its own, so the same character always produces the same block (`"aa"` → two identical blocks). The modulus `N = P × Q` must also exceed every character code in the message; see [Choosing N large enough](algorithm.md#choosing-n-large-enough).

---

## High-Level Flow

```
User Input (plaintext string)
        │
        ▼
  For each character:
    ASCII value  ──► RSA encryption (C = M^E mod N) ──► zero-padded numeric block
        │
        ▼
  Encrypted message (concatenated numeric blocks)

Encrypted message (numeric blocks)
        │
        ▼
  For each block:
    Parse integer ──► RSA decryption (M = C^D mod N) ──► chr() ──► character
        │
        ▼
  Plaintext string (recovered)
```

Both the encryption and decryption exponentiation steps use the **square-and-multiply** algorithm, driven by the `EncryptionTable` class, which decomposes the exponent into powers of 2 and performs modular squarings in sequence.

---

## Version History

| Version | Status | Notes |
|---|---|---|
| 0.1.0 | Alpha | Initial release — core RSA encrypt/decrypt + CLI (the CLI entry point has a [known import issue](cli.md#known-issue-in-v010)) |

