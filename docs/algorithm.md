# Algorithm

This document explains the mathematics and implementation details of the RSA cipher as used in NPcryption.

---

## Background: RSA Cryptography

RSA is an asymmetric public-key cryptosystem invented by Rivest, Shamir, and Adleman (1977). It is based on the practical difficulty of factoring the product of two large prime numbers.

In classical RSA:
- A **public key** `(N, E)` is shared openly and used to encrypt.
- A **private key** `(N, D)` is kept secret and used to decrypt.

In NPcryption both parties supply P, Q, and E directly — so the "asymmetry" is collapsed into a shared-secret usage pattern, which is appropriate for its educational purpose.

---

## Key Parameters

| Symbol | Name | Description |
|---|---|---|
| `P` | Prime 1 | First private prime number |
| `Q` | Prime 2 | Second private prime number |
| `N` | Modulus | `N = P × Q` |
| `φ(N)` | Totient | `φ(N) = (P−1) × (Q−1)` |
| `E` | Public exponent | Must be coprime with φ(N) and `1 < E < φ(N)` |
| `D` | Private exponent | Modular inverse of E mod φ(N): `E × D ≡ 1 (mod φ(N))` |

### Choosing N large enough

Each character is encrypted as its own number `M = ord(character)`, and RSA only recovers values in the range `0 … N−1`. Every character in the message must therefore satisfy **`ord(character) < N`**:

| Character set | Minimum N | Example keys |
|---|---|---|
| Printable ASCII (32–126) | 127 | `P=11, Q=13` (N=143), `P=17, Q=19` (N=323) |
| Latin-1 (up to 255) | 256 | `P=17, Q=19` (N=323), `P=61, Q=53` (N=3233) |

If `ord(character) ≥ N`, the character is silently reduced modulo N and decrypts to a different character. NPcryption does not check this, nor does it check that P and Q are prime or that E is coprime with φ(N).

---

## Encryption

For each character in the plaintext:

1. **ASCII conversion** — obtain the integer `M = ord(character)`.
2. **Modular exponentiation** — compute `C = M^E mod N`.
3. **Zero-padding** — pad `C` with leading zeros so it is exactly `len(str(N))` digits wide. This ensures every character maps to a fixed-width block, allowing the ciphertext to be reliably split during decryption.

The final ciphertext is the concatenation of all padded blocks.

### Example

```
P = 17, Q = 19  →  N = 323,  φ(N) = 288
E = 5

Character 'H'  →  M = 72
C = 72^5 mod 323

Binary expansion of E = 5 = 4 + 1 = (101)₂
  k=0: 72            mod 323 = 72      (power 1 is valid)
  k=1: 72² = 5184    mod 323 = 16      (power 2 is not used)
  k=2: 16² = 256     mod 323 = 256     (power 4 is valid)
product = 72 × 256 = 18432
C = 18432 mod 323 = 21

Padded to len("323") = 3 digits → "021"
```

So `encrypt(17, 19, 5, "H") == "021"`, and `encrypt(17, 19, 5, "Hello") == "021271109109042"`.

---

## Decryption

For each fixed-width block in the ciphertext:

1. **Parse integer** — `C = int(block)`.
2. **Compute private exponent D** (once, via Extended Euclidean Algorithm — see below).
3. **Modular exponentiation** — compute `M = C^D mod N`.
4. **Character recovery** — `character = chr(M)`.

### Example (continuing from above)

```
D such that 5D ≡ 1 (mod 288)  →  D = 173      (5 × 173 = 865 = 3 × 288 + 1)

C = 21
D = 173 = 128 + 32 + 8 + 4 + 1 = (10101101)₂

  k=0: 21                    mod 323 = 21     (power 1 is valid)
  k=1: 21²  = 441            mod 323 = 118
  k=2: 118² = 13924          mod 323 = 35     (power 4 is valid)
  k=3: 35²  = 1225           mod 323 = 256    (power 8 is valid)
  k=4: 256² = 65536          mod 323 = 290
  k=5: 290² = 84100          mod 323 = 120    (power 32 is valid)
  k=6: 120² = 14400          mod 323 = 188
  k=7: 188² = 35344          mod 323 = 137    (power 128 is valid)
product = 21 × 35 × 256 × 120 × 137 = 3093350400
M = 3093350400 mod 323 = 72
chr(72) = 'H'  ✓
```

---

## Square-and-Multiply (Fast Modular Exponentiation)

Computing `M^E mod N` naively requires E multiplications. For large E this is impractical. NPcryption instead uses **binary (square-and-multiply) exponentiation**, which requires only O(log E) squarings.

### Algorithm

Given base `M`, exponent `E`, modulus `N`:

1. Write `E` in binary: `E = b_k b_{k-1} … b_1 b_0` where `b_k = 1`.
2. Build a table of successive squarings:
   ```
   row 0:  M^1       mod N
   row 1:  M^2       mod N   = (row 0)^2 mod N
   row 2:  M^4       mod N   = (row 1)^2 mod N
   row 3:  M^8       mod N   = (row 2)^2 mod N
   ...
   ```
3. Multiply together only those rows whose corresponding bit in `E` is `1`:
   ```
   M^E mod N = (product of selected modNums) mod N
   ```

NPcryption multiplies all of the selected rows together first and reduces modulo N once at the end, rather than after each multiplication. Python's arbitrary-precision integers keep this correct; the intermediate product just gets larger.

### Implementation: `EncryptionTable`

`EncryptionTable(n)` builds this table for exponent `n`:

- **`split_into_valid_powers_of_2(n)`** — returns the powers of 2 whose sum equals `n` (i.e., the set bits).
- **`get_highest_power_of_2(n)`** — returns `2^⌊log₂(n)⌋`, the highest power needed.
- `initialize(n)` — populates `self.power`, `self.prevSQR`, `self.modNum`, and `self.validity` arrays.
- `set_prev_sqr(value, k)` / `set_mod_num(value, k)` — filled in by the calling encryption/decryption function during the squaring loop.
- `get_product()` — multiplies `modNum[k]` for every row `k` where `validity[k] == True`.
- `get_length()` — returns the number of rows (= number of squarings needed).

```python
# Conceptual example: E = 5 = (101)₂
# power    = [1, 2, 4]
# validity = [True, False, True]
# get_product() = modNum[0] * modNum[2]
```

> **Odd exponents only.** For an even `n` the table starts at power 2 instead of 1, but the callers still seed row 0 with `M¹`, so the result is wrong (e.g. `n = 6` yields `M³`). This never matters for valid RSA keys: φ(N) is even, so both `E` and `D` are always odd.

---

## Private Exponent Derivation: Extended Euclidean Algorithm

To decrypt, NPcryption must first find `D` such that:

```
E × D ≡ 1  (mod φ(N))
```

This is equivalent to finding the **modular inverse** of `E` in `ℤ_{φ(N)}`. The **Extended Euclidean Algorithm (EEA)** computes it by tracking Bézout coefficients throughout the GCD computation.

### `DTable` Implementation

`DTable(φN, E)` maintains four lists:

| Column | Initial values | Recurrence |
|---|---|---|
| `R` (remainders) | `[φN, E, …]` | `R[i] = R[i-2] mod R[i-1]` |
| `Q` (quotients) | `[0, 0, …]` | `Q[i] = R[i-2] // R[i-1]` |
| `X` | `[1, 0, …]` | `X[i] = X[i-2] − X[i-1] × Q[i]` |
| `D` | `[0, 1, …]` | `D[i] = D[i-2] − D[i-1] × Q[i]` |

`generateTable()` continues until `R[i]` reaches `1` or `0`. Reaching `0` means `E` was not coprime with φ(N); the resulting `D` is meaningless but no error is raised.

`getD(φN)` returns the last `D` value, adjusting it to be positive (by adding `φN` if negative).

#### Worked example: `DTable(288, 5)`

| i | R | Q | X | D |
|---|---|---|---|---|
| 0 | 288 | 0 | 1 | 0 |
| 1 | 5 | 0 | 0 | 1 |
| 2 | 3 | 57 | 1 | −57 |
| 3 | 2 | 1 | −1 | 58 |
| 4 | 1 | 1 | 2 | −115 |

The remainder reaches 1 at row 4, so `D = −115 + 288 = 173`. Check: `288 × 2 + 5 × (−115) = 1`.

### `DecryptionTable`

`DecryptionTable` is a subclass of `EncryptionTable`:
1. Calls `DecryptionTable.getD(φN, E)`, which instantiates `DTable(φN, E)` and calls `generateTable()`.
2. Extracts `D = dtable.getD(φN)`.
3. Calls `super().__init__(D)` — so the same square-and-multiply machinery operates with exponent `D` instead of `E`.

---

## Ciphertext Block Width

Because `C = M^E mod N` and `N = P × Q`, the value of `C` is always in the range `[0, N−1]`. The number of decimal digits in `C` can vary. To allow reliable parsing during decryption, every cipher block is **left-padded with zeros** to exactly `len(str(N))` digits:

```python
while len(str(EncryptedChar)) != len(str(PQ)):
    EncryptedChar = "0" + EncryptedChar
```

During decryption, the message is split into chunks of that same fixed width:

```python
CharLength = len(str(PQ))
for eachCharCoded in range(0, len(message), CharLength):
    codedChar = int(message[eachCharCoded : eachCharCoded + CharLength])
```

---

## Character Caching

Both `encrypt()` and `decrypt()` maintain an in-memory dictionary to avoid recomputing the same character more than once within a single call:

```python
encyptedDict = {}   # Encryption.py: maps plaintext char → cipher block string
decryptDict  = {}   # Decryption.py:  maps cipher int   → plaintext char
```

This is a simple memoization optimization — useful when the same character appears many times in the message.

---

## Complexity

| Operation | Complexity |
|---|---|
| Single character encryption | O(log E) squarings |
| Single character decryption | O(log D) squarings |
| `DTable.generateTable()` | O(log(min(φN, E))) steps (Euclidean algorithm) |
| Full message encryption/decryption | O(unique_chars × log(exponent)) |

