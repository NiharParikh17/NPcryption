# API Reference

Complete reference for every public module, class, and function in NPcryption.

---

## Package: `npcryption`

**File:** `src/npcryption/__init__.py`

The top-level package. Imports and re-exports the two primary public functions.

```python
from npcryption import encrypt, decrypt
```

### `__version__`
```python
__version__: str = "0.1.0"
```
Current package version string.

### `__all__`
```python
__all__ = ["encrypt", "decrypt"]
```

---

## `npcryption.core.Encryption`

**File:** `src/npcryption/core/Encryption.py`

Provides RSA encryption at the string level.

---

### `encrypt(P, Q, E, message) → str`

Encrypts a plaintext string using RSA.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `P` | `int` | First prime factor of the RSA modulus (private) |
| `Q` | `int` | Second prime factor of the RSA modulus (private) |
| `E` | `int` | Public key exponent; must be coprime with `(P-1)*(Q-1)` |
| `message` | `str` | Plaintext string to encrypt |

**Returns**  
`str` — Ciphertext as a string of zero-padded numeric blocks concatenated together. Each block has exactly `len(str(P * Q))` digits.

**Example**
```python
from npcryption import encrypt

cipher = encrypt(3, 11, 7, "Hi")
# Returns a string of numeric blocks, e.g. "3203"
```

**Notes**
- Characters are processed one at a time via `encryptCharacter()`.
- An internal dictionary caches already-encrypted characters to avoid redundant computation.
- `N = P * Q` is computed once and reused for all characters.
- The `EncryptionTable` is instantiated once with exponent `E` and reused per character.

---

### `encryptCharacter(PQ, character, powers) → str`

Encrypts a single character using modular exponentiation.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `PQ` | `int` | The RSA modulus `N = P * Q` |
| `character` | `str` | A single character to encrypt |
| `powers` | `EncryptionTable` | Pre-built squaring table for exponent E |

**Returns**  
`str` — Zero-padded ciphertext block for this character (length = `len(str(PQ))`).

**Algorithm**
1. Get `M = ord(character)`.
2. Seed the table: `prevSQR[0] = M`, `modNum[0] = M % PQ`.
3. For each subsequent row: `prevSQR[k] = modNum[k-1]^2`, `modNum[k] = prevSQR[k] % PQ`.
4. `C = getProduct() % PQ`.
5. Left-pad `C` with `'0'` until `len(str(C)) == len(str(PQ))`.

---

### `getAscii(character) → int`

Returns the Unicode code point (ASCII value) of a character via `ord()`.

---

### `getCharacter(ascii) → str`

Returns the character corresponding to a Unicode code point via `chr()`.

---

## `npcryption.core.Decryption`

**File:** `src/npcryption/core/Decryption.py`

Provides RSA decryption at the string level.

---

### `decrypt(P, Q, E, message) → str`

Decrypts an NPcryption ciphertext string back to plaintext.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `P` | `int` | First prime factor of the RSA modulus (private) |
| `Q` | `int` | Second prime factor of the RSA modulus (private) |
| `E` | `int` | Public key exponent used during encryption |
| `message` | `str` | Ciphertext string produced by `encrypt()` |

**Returns**  
`str` — Recovered plaintext string.

**Notes**
- `N = P * Q` is computed and used to determine block width: `CharLength = len(str(PQ))`.
- Private exponent `D` is derived automatically via `DecryptionTable((P-1)*(Q-1), E)`.
- An internal dictionary caches already-decrypted blocks.

**Example**
```python
from npcryption import decrypt

plain = decrypt(3, 11, 7, "3203")
# Returns "Hi"
```

---

### `decryptCharacter(PQ, codedChar, powers) → str`

Decrypts a single ciphertext integer using modular exponentiation with the private exponent.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `PQ` | `int` | The RSA modulus `N = P * Q` |
| `codedChar` | `int` | Integer value of a single cipher block |
| `powers` | `DecryptionTable` | Pre-built squaring table for private exponent D |

**Returns**  
`str` — The recovered plaintext character.

---

### `getAscii(character) → int`

Same as in `Encryption.py` — returns `ord(character)`.

---

### `getCharacter(ascii) → str`

Same as in `Encryption.py` — returns `chr(ascii)`.

---

## `npcryption.core.EncryptionTable`

**File:** `src/npcryption/core/EncryptionTable.py`

The square-and-multiply exponentiation engine. Used directly for encryption and indirectly (via inheritance) for decryption.

---

### `class EncryptionTable`

#### `__init__(self, n: int)`

Initializes the table for exponent `n`.

**Attributes**

| Attribute | Type | Description |
|---|---|---|
| `power` | `list[int]` | Powers of 2: `[1, 2, 4, 8, …]` up to highest power ≤ n |
| `prevSQR` | `list[int]` | The value before squaring at each step (filled by caller) |
| `modNum` | `list[int]` | `prevSQR % N` at each step (filled by caller) |
| `validity` | `list[bool]` | `True` if this power-of-2 appears in the binary expansion of `n` |

#### `initialize(self, n: int) → None`

Populates all four lists. Calls `splitIntoValidPowersOf2(n)` and `getHighestPowerOf2(n)` to determine row count and validity.

**Starting power:**
- `1` if `n` is odd
- `2` if `n` is even

#### `setPrevSQR(self, value: int, index: int) → None`

Sets `self.prevSQR[index] = value`.

#### `setModNum(self, value: int, index: int) → None`

Sets `self.modNum[index] = value`.

#### `getProduct(self) → int`

Returns the product of `modNum[k]` for all `k` where `validity[k] is True`.

```python
product = 1
for k in range(len(self.power)):
    if self.validity[k]:
        product *= self.modNum[k]
return product
```

#### `getLength(self) → int`

Returns the number of rows in the table (= number of squaring iterations needed).

---

### Module-level functions

#### `splitIntoValidPowersOf2(n: int) → list[int]`

Returns the list of powers of 2 whose sum equals `n` (the set bits of `n`).

```python
splitIntoValidPowersOf2(7)  # → [1, 2, 4]
splitIntoValidPowersOf2(6)  # → [2, 4]
```

#### `getHighestPowerOf2(n: int) → int`

Returns `2^⌊log₂(n)⌋` — the largest power of 2 that is ≤ n.

```python
getHighestPowerOf2(7)  # → 4
getHighestPowerOf2(8)  # → 8
```

---

## `npcryption.core.DecryptionTable`

**File:** `src/npcryption/core/DecryptionTable.py`

Derives the RSA private exponent `D` and inherits `EncryptionTable`'s square-and-multiply machinery.

---

### `class DecryptionTable(EncryptionTable)`

Subclass of `EncryptionTable`.

#### `__init__(self, PQ: int, E: int)`

**Parameters**

| Name | Type | Description |
|---|---|---|
| `PQ` | `int` | φ(N) = `(P-1) * (Q-1)` |
| `E` | `int` | Public key exponent |

1. Calls `DecryptionTable.getD(PQ, E)` to compute `D`.
2. Calls `super().__init__(D)` — initializes the squaring table for exponent `D`.

#### `getD(P_Q: int, E: int) → int` *(static method)*

Instantiates `DTable(P_Q, E)`, calls `generateTable()`, and returns `dtable.getD(P_Q)`.

---

## `npcryption.core.DTable`

**File:** `src/npcryption/core/DTable.py`

Implements the Extended Euclidean Algorithm to compute the modular inverse of `E` mod `φ(N)`.

---

### `class DTable`

#### `__init__(self, PQ: int, E: int)`

Initializes the algorithm state.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `PQ` | `int` | φ(N) = `(P-1)*(Q-1)` — the Euler totient |
| `E` | `int` | Public key exponent |

**Initial state**

| List | Index 0 | Index 1 |
|---|---|---|
| `R` | `PQ` (= φN) | `E` |
| `X` | `1` | `0` |
| `D` | `0` | `1` |
| `Q` | `0` | `0` |

#### `generateTable(self) → None`

Runs the Extended Euclidean Algorithm. At each row `i ≥ 2`:

```
R[i] = R[i-2] % R[i-1]
Q[i] = R[i-2] // R[i-1]
X[i] = X[i-2] - X[i-1] * Q[i]
D[i] = D[i-2] - D[i-1] * Q[i]
```

Continues while the latest remainder is neither `1` nor `0`.

#### `getD(self, PQ: int) → int`

Returns the last computed `D` value. If `D < 0`, adds `PQ` to ensure a positive result.

```python
D = self.D[-1]
if D < 0:
    D = D + PQ
return D
```

---

## `npcryption.cli`

**File:** `src/npcryption/cli.py`

Interactive command-line interface.

---

### `encrypt(P, Q, E, message) → str`

Thin wrapper around `Encryption.encrypt`. Used by `main()`.

### `decrypt(P, Q, E, message) → str`

Thin wrapper around `Decryption.decrypt`. Used by `main()`.

### `main() → None`

The CLI entry point. Called when the user runs `npcryption` from the terminal (via the `[project.scripts]` entry point in `pyproject.toml`).

**Interactive prompts:**

```
Press E for Encryption or D for Decryption:
Enter Private Key P:
Enter Private Key Q:
Enter Public Key E:
Enter Message:          ← (encryption only)
Encrypted Message:      ← (decryption only)
```

Prints the encrypted or decrypted result to stdout.

