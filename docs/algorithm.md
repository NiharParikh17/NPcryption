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

---

## Encryption

For each character in the plaintext:

1. **ASCII conversion** — obtain the integer `M = ord(character)`.
2. **Modular exponentiation** — compute `C = M^E mod N`.
3. **Zero-padding** — pad `C` with leading zeros so it is exactly `len(str(N))` digits wide. This ensures every character maps to a fixed-width block, allowing the ciphertext to be reliably split during decryption.

The final ciphertext is the concatenation of all padded blocks.

### Example

```
P = 3, Q = 11  →  N = 33,  φ(N) = 20
E = 7

Character 'A'  →  M = 65
C = 65^7 mod 33

Binary expansion of E = 7 = 4 + 2 + 1 = (111)₂
  k=0: 65^1  mod 33 = 65 mod 33 = 32       (power 1 is valid)
  k=1: 32^2  mod 33 = 1024 mod 33 = 1       (power 2 is valid)  
  k=2: 1^2   mod 33 = 1 mod 33 = 1          (power 4 is valid)
product = 32 × 1 × 1 = 32
C = 32 mod 33 = 32

Padded to len("33")=2 digits → "32"
```

---

## Decryption

For each fixed-width block in the ciphertext:

1. **Parse integer** — `C = int(block)`.
2. **Compute private exponent D** (once, via Extended Euclidean Algorithm — see below).
3. **Modular exponentiation** — compute `M = C^D mod N`.
4. **Character recovery** — `character = chr(M)`.

### Example (continuing from above)

```
D such that 7D ≡ 1 (mod 20)  →  D = 3

C = 32
M = 32^3 mod 33 = 32768 mod 33 = 65
chr(65) = 'A'  ✓
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

### Implementation: `EncryptionTable`

`EncryptionTable(n)` builds this table for exponent `n`:

- **`splitIntoValidPowersOf2(n)`** — returns the powers of 2 whose sum equals `n` (i.e., the set bits).
- **`getHighestPowerOf2(n)`** — returns `2^⌊log₂(n)⌋`, the highest power needed.
- `initialize(n)` — populates `self.power`, `self.prevSQR`, `self.modNum`, and `self.validity` arrays.
- `setPrevSQR(value, k)` / `setModNum(value, k)` — filled in by the calling encryption/decryption function during the squaring loop.
- `getProduct()` — multiplies `modNum[k]` for every row `k` where `validity[k] == True`.
- `getLength()` — returns the number of rows (= number of squarings needed).

```python
# Conceptual example: E = 7 = (111)₂
# powers = [1, 2, 4], all valid
# validity = [True, True, True]
# getProduct() = modNum[0] * modNum[1] * modNum[2]
```

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

`generateTable()` continues until `R[i]` reaches `1` or `0`.

`getD(φN)` returns the last `D` value, adjusting it to be positive (by adding `φN` if negative).

### `DecryptionTable`

`DecryptionTable` is a subclass of `EncryptionTable`:
1. Instantiates `DTable(φN, E)` and calls `generateTable()`.
2. Extracts `D = dtable.getD(φN)`.
3. Calls `EncryptionTable.__init__(D)` — so the same square-and-multiply machinery operates with exponent `D` instead of `E`.

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

