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

cipher = encrypt(17, 19, 5, "Hi")
# "021022"  (N = 323, so each block is 3 digits: 'H' → "021", 'i' → "022")
```

**Notes**
- Characters are processed one at a time via `encryptCharacter()`.
- An internal dictionary caches already-encrypted characters to avoid redundant computation.
- `N = P * Q` is computed once and reused for all characters.
- The `EncryptionTable` is instantiated once with exponent `E` and reused per character.
- Every character's code point must be **less than `N`**. Larger values are silently reduced modulo `N` and will not decrypt back to the original character. `N ≥ 127` covers all printable ASCII.
- The keys are not validated: if `P`/`Q` are not prime or `E` is not coprime with `(P-1)*(Q-1)`, a ciphertext is still returned but it will not round-trip.

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
4. `C = powers.get_product() % PQ`.
5. Left-pad `C` with `'0'` until `len(str(C)) == len(str(PQ))`.

---

### `getAscii(character) → int`

Returns the Unicode code point (ASCII value) of a character via `ord()`.

---

### `getCharacter(ascii) → str`

Returns the character corresponding to a Unicode code point via `chr()`. Defined for symmetry with `Decryption.py`; `encrypt()` does not use it.

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
- `message` must contain only digits. Any other character makes `int()` raise `ValueError`.

**Example**
```python
from npcryption import decrypt

plain = decrypt(17, 19, 5, "021022")
# "Hi"
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

Same as in `Encryption.py`: returns `ord(character)`. `decrypt()` does not use it.

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

Populates all four lists. Calls `split_into_valid_powers_of_2(n)` and `get_highest_power_of_2(n)` to determine row count and validity.

**Starting power:**
- `1` if `n` is odd
- `2` if `n` is even

> **Note:** The callers always seed row 0 with `M¹`, so the table only gives the correct result for **odd** exponents. In valid RSA keys both `E` and `D` are always odd (φ(N) is even), so this path is not hit in normal use. For example, `EncryptionTable(6)` has `power == [2, 4]` and computes `M³` rather than `M⁶`.

#### `set_prev_sqr(self, value: int, index: int) → None`

Sets `self.prevSQR[index] = value`.

#### `set_mod_num(self, value: int, index: int) → None`

Sets `self.modNum[index] = value`.

#### `get_product(self) → int`

Returns the product of `modNum[k]` for all `k` where `validity[k] is True`. The product is **not** reduced modulo `N`; callers apply `% PQ` to the result.

```python
product = 1
for index in range(0, len(self.power)):
    if self.validity[index]:
        product *= self.modNum[index]
return product
```

#### `get_length(self) → int`

Returns the number of rows in the table (= number of squaring iterations needed).

---

### Module-level functions

#### `split_into_valid_powers_of_2(n: int) → list[int]`

Returns the list of powers of 2 whose sum equals `n` (the set bits of `n`).

```python
split_into_valid_powers_of_2(7)  # → [1, 2, 4]
split_into_valid_powers_of_2(6)  # → [2, 4]
```

#### `get_highest_power_of_2(n: int) → int`

Returns `2^⌊log₂(n)⌋` — the largest power of 2 that is ≤ n. Uses `math.log`, so `n` must be positive.

```python
get_highest_power_of_2(7)  # → 4
get_highest_power_of_2(8)  # → 8
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

#### `getD(P_Q: int, E: int) → int`

Instantiates `DTable(P_Q, E)`, calls `generateTable()`, and returns `dtable.getD(P_Q)`.

Defined without `@staticmethod`, so it must be called on the class (`DecryptionTable.getD(phi, E)`), as `__init__` does. Calling it on an instance binds the instance to `P_Q` and raises `TypeError`.

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

Continues while the latest remainder is neither `1` nor `0`. A final remainder of `0` means `gcd(φN, E) ≠ 1` (an invalid `E`); no error is raised in that case.

Calling it a second time appends a duplicate copy of the rows to each list (the value returned by `getD()` is unchanged).

#### `getD(self, PQ: int) → int`

Returns the last computed `D` value. If `D < 0`, adds `PQ` to ensure a positive result.

```python
D = (self.D[len(self.D) - 1])
if D < 0:
    D = D + PQ
return D
```

**Example**
```python
from npcryption.core.DTable import DTable

dt = DTable(288, 5)    # φ(N) for P=17, Q=19; E=5
dt.generateTable()
dt.getD(288)           # → 173   (5 × 173 = 865 = 3 × 288 + 1)
```

---

## `npcryption.cli`

**File:** `src/npcryption/cli.py`

Interactive command-line interface. Imports `Encryption` and `Decryption` from `npcryption.core`. Importing the module has no side effects; `main()` only runs automatically when the module is executed as a script (`python -m npcryption.cli`).

---

### `encrypt(P, Q, E, message) → str`

Thin wrapper around `Encryption.encrypt`. Used by `main()`.

### `decrypt(P, Q, E, message) → str`

Thin wrapper around `Decryption.decrypt`. Used by `main()`.

### `main() → None`

The CLI entry point. Called when the user runs `npcryption` from the terminal (via the `[project.scripts]` entry point in `pyproject.toml`) or `python -m npcryption.cli`.

**Interactive prompts:**

```
Press E for Encryption or D for Decryption:
Enter Private Key P:
Enter Private Key Q:
Enter Public Key E:
Enter Message:          ← (encryption only)
Encrypted Message:      ← (decryption only)
```

Prints the encrypted or decrypted result to stdout. `P`, `Q` and `E` are read before the choice is checked; any choice other than `E`/`e`/`D`/`d` prints nothing.

