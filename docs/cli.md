# CLI Guide

NPcryption ships with an interactive command-line interface that lets you encrypt and decrypt messages without writing any Python code.

---

## Running the CLI

### After installation

The console script registered in `pyproject.toml` calls `npcryption.cli:main`:

```bash
pip install -e .
npcryption
```

### As a module

Equivalent, and works wherever the package is importable:

```bash
python -m npcryption.cli
```

Importing `npcryption.cli` from Python does **not** start the prompt; call `npcryption.cli.main()` to run it.

---

## Interactive Session

You will be prompted step by step.

### Step 1 — Choose operation

```
Press E for Encryption or D for Decryption:
```

Type `E` (or `e`) to encrypt, or `D` (or `d`) to decrypt. Press Enter.

### Step 2 — Enter key parameters

```
Enter Private Key P:
Enter Private Key Q:
Enter Public Key E:
```

- `P` and `Q` must be **distinct prime numbers**.
- `E` must be **coprime** with `(P−1) × (Q−1)`.
- `N = P × Q` must be **larger than the code point of every character** in the message (at least 127 for printable ASCII).
- All three must be **integers**; anything else raises `ValueError`.

The key parameters are read before the choice from step 1 is checked. If you typed anything other than `E`, `e`, `D` or `d`, the CLI exits after this step without printing anything.

> **Important:** You must use the **same P, Q, and E values** for both encryption and decryption of the same message.

### Step 3 — Enter the message

**Encryption:**
```
Enter Message:
```
Type the plaintext string you want to encrypt. Press Enter.

**Decryption:**
```
Encrypted Message:
```
Paste the numeric ciphertext string produced by a previous encryption. Press Enter.

### Step 4 — Result

The encrypted ciphertext (or recovered plaintext) is printed to the terminal.

---

## Example Session — Encryption

```
$ npcryption
Press E for Encryption or D for Decryption: E
Enter Private Key P: 17
Enter Private Key Q: 19
Enter Public Key E: 5
Enter Message: Hello
021271109109042
```

N = 323 has three digits, so each character becomes a three-digit block: `021` `271` `109` `109` `042`.

---

## Example Session — Decryption

```
$ npcryption
Press E for Encryption or D for Decryption: D
Enter Private Key P: 17
Enter Private Key Q: 19
Enter Public Key E: 5
Encrypted Message: 021271109109042
Hello
```

---

## Choosing Valid Key Parameters

| Requirement | Rule |
|---|---|
| P and Q must be prime | e.g. 11, 13, 17, 19, 53, 61, 101, 103 … |
| P ≠ Q | Using the same prime twice degrades security |
| `gcd(E, (P-1)*(Q-1)) == 1` | E must be coprime with the totient |
| `1 < E < (P-1)*(Q-1)` | E must lie in this range |
| `N = P*Q > ord(c)` for every character `c` | Otherwise the character cannot be recovered |

None of these rules are checked by NPcryption. Invalid keys still produce a ciphertext, but it will not decrypt to the original message.

### Common valid combinations

All of these have N ≥ 127, so they work for any printable ASCII message.

| P | Q | N | φ(N) | Valid E values (sample) |
|---|---|---|---|---|
| 11 | 13 | 143 | 120 | 7, 11, 13, 17, 19, 23, 29, 31 |
| 17 | 19 | 323 | 288 | 5, 7, 11, 13, 17, 19, 23, 25 |
| 61 | 53 | 3233 | 3120 | 7, 11, 17, 19, 23, 29, 31, 37 |
| 101 | 103 | 10403 | 10200 | 7, 11, 13, 19, 23, 29, 31, 37 |

---

## Limitations

- All inputs are read from stdin; there is no support for file input or command-line flags yet.
- Characters are encrypted individually via their code point. Any character whose code point is ≥ N (for example most non-ASCII characters with small keys) will not decrypt correctly.
