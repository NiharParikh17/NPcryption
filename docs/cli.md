# CLI Guide

NPcryption ships with an interactive command-line interface that lets you encrypt and decrypt messages without writing any Python code.

---

## Running the CLI

### After installation

```bash
pip install -e .
npcryption
```

### Without installation (from the project root)

```bash
python src/npcryption/cli.py
```

---

## Interactive Session

When you run `npcryption` you will be prompted step by step.

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
- All three must be **positive integers**.

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
Enter Private Key P: 3
Enter Private Key Q: 11
Enter Public Key E: 7
Enter Message: Hello
3203030303
```

*(Output is illustrative.)*

---

## Example Session — Decryption

```
$ npcryption
Press E for Encryption or D for Decryption: D
Enter Private Key P: 3
Enter Private Key Q: 11
Enter Public Key E: 7
Encrypted Message: 3203030303
Hello
```

*(Output is illustrative.)*

---

## Choosing Valid Key Parameters

| Requirement | Rule |
|---|---|
| P and Q must be prime | e.g. 3, 5, 7, 11, 13, 17, 19, 23 … |
| P ≠ Q | Using the same prime twice degrades security |
| `gcd(E, (P-1)*(Q-1)) == 1` | E must be coprime with the totient |
| `1 < E < (P-1)*(Q-1)` | E must lie in this range |

### Common valid combinations

| P | Q | N | φ(N) | Valid E values (sample) |
|---|---|---|---|---|
| 3 | 11 | 33 | 20 | 3, 7, 9, 11, 13, 17, 19 |
| 5 | 11 | 55 | 40 | 3, 7, 9, 11, 13, 17, 21, 23 |
| 7 | 11 | 77 | 60 | 7, 11, 13, 17, 19, 23, 29, 31 |
| 11 | 13 | 143 | 120 | 7, 11, 13, 17, 23, 37, 41, 43 |

---

## Limitations

- The CLI calls `main()` at module import time (`main()` is called at the bottom of `cli.py`). This means importing `cli` directly will trigger the interactive prompt.
- All inputs are read from stdin; there is no support for file input or command-line flags in v0.1.0.
- Characters are encrypted individually via their ASCII code. Non-ASCII (Unicode) characters may produce unexpected results if their code point exceeds N.

