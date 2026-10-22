"""
Bridge between the NPcryption library and the web demo; runs in Pyodide.

Every number the page shows comes from the library's own functions and
tables. This module only validates input, collects the intermediate values
the library computes, and returns them as JSON for app.js. Values that can
exceed JavaScript's safe integer range are returned as strings.
"""
import itertools
import json
import math

import npcryption
from npcryption.core.DTable import DTable
from npcryption.core.Decryption import decryptCharacter
from npcryption.core.DecryptionTable import DecryptionTable
from npcryption.core.Encryption import encryptCharacter
from npcryption.core.EncryptionTable import EncryptionTable

MAX_PRIME = 9973
MAX_MESSAGE = 60
EXPONENT_CHOICES = 10


def is_prime(n):
    """Return True if `n` is prime (trial division, fine for small `n`)."""
    if n < 2:
        return False
    return all(n % d for d in range(2, math.isqrt(n) + 1))


def smallest_factor(n):
    """Return the smallest factor of `n` above 1 and how many divisors were tried."""
    tries = 0
    for d in range(2, math.isqrt(n) + 1):
        tries += 1
        if n % d == 0:
            return d, tries
    return n, tries


def ladder(table):
    """Return the rows of a square-and-multiply table the library has filled in."""
    return [
        {"power": power, "square": str(square), "value": str(value), "used": used}
        for power, square, value, used in zip(
            table.power, table.prevSQR, table.modNum, table.validity)
    ]


def _prime_error(n):
    """Return why `n` cannot be used as P or Q, or None if it can."""
    if not 2 <= n <= MAX_PRIME:
        return f"Use a prime between 2 and {MAX_PRIME}."
    if not is_prime(n):
        factor, _ = smallest_factor(n)
        return f"{n} isn't prime: it's {factor} × {n // factor}."
    return None


def keys(P, Q, E):
    """Validate (P, Q, E) and derive N, phi(N), suggested exponents and D."""
    errors = {}
    for field, n in (("p", P), ("q", Q)):
        error = _prime_error(n)
        if error:
            errors[field] = error
    if not errors and P == Q:
        errors["q"] = "Pick a prime different from P. RSA needs two distinct primes."
    result = {"p": P, "q": Q, "e": E, "errors": errors}
    if errors:
        return result

    N = P * Q
    phi = (P - 1) * (Q - 1)
    coprime = (e for e in range(3, phi, 2) if math.gcd(e, phi) == 1)
    choices = list(itertools.islice(coprime, EXPONENT_CHOICES))
    result.update(n=N, phi=phi, width=len(str(N)), choices=choices)
    if not choices:
        errors["e"] = "No public exponent works with primes this small. Pick larger primes."
    elif not 1 < E < phi:
        errors["e"] = f"E must be between 2 and {phi - 1}."
    elif math.gcd(E, phi) != 1:
        errors["e"] = (f"{E} shares the factor {math.gcd(E, phi)} with φ(N) = {phi}, "
                       "so it has no matching private exponent.")
    if errors:
        return result

    table = DTable(phi, E)
    table.generateTable()
    result.update(
        d=table.getD(phi),
        euclid=[{"r": r, "q": q, "x": x, "d": d}
                for r, q, x, d in zip(table.R, table.Q, table.X, table.D)],
    )
    return result


def encrypt_steps(P, Q, E, message):
    """Encrypt `message` one character at a time, keeping each character's table."""
    key = keys(P, Q, E)
    if key["errors"]:
        return {"keys": key}
    message = message[:MAX_MESSAGE]
    chars = []
    for character in message:
        table = EncryptionTable(E)
        block = encryptCharacter(key["n"], character, table)
        chars.append({
            "char": character,
            "code": ord(character),
            "fits": ord(character) < key["n"],
            "block": block,
            "ladder": ladder(table),
            "product": str(table.get_product()),
        })
    return {
        "keys": key,
        "chars": chars,
        "ciphertext": npcryption.encrypt(P, Q, E, message),
    }


def decrypt_steps(P, Q, E, ciphertext):
    """Decrypt `ciphertext` block by block, keeping each block's table."""
    key = keys(P, Q, E)
    if key["errors"]:
        return {"keys": key}
    N, width = key["n"], key["width"]
    text = "".join(ciphertext.split())
    if not (text.isascii() and text.isdigit()) and text:
        return {"keys": key, "error": "The ciphertext can only contain digits."}
    if len(text) % width:
        return {"keys": key, "error": (
            f"N = {N} has {width} digits, so the ciphertext must be made of "
            f"{width}-digit blocks. This one has {len(text)} digits.")}

    blocks = []
    for start in range(0, len(text), width):
        value = int(text[start:start + width])
        table = DecryptionTable(key["phi"], E)
        try:
            character = decryptCharacter(N, value, table)
        except ValueError:
            character = None
        blocks.append({
            "block": text[start:start + width],
            "value": value,
            "fits": value < N,
            "code": table.get_product() % N,
            "char": character,
            "ladder": ladder(table),
            "product": str(table.get_product()),
        })
    readable = all(block["char"] is not None for block in blocks)
    return {
        "keys": key,
        "blocks": blocks,
        "plaintext": npcryption.decrypt(P, Q, E, text) if readable else None,
    }


def crack(P, Q, E):
    """Recover D from the public key (N, E) alone by factoring N."""
    key = keys(P, Q, E)
    if key["errors"]:
        return {"keys": key}
    factor, tries = smallest_factor(key["n"])
    other = key["n"] // factor
    phi = (factor - 1) * (other - 1)
    return {"keys": key, "factor": factor, "other": other, "tries": tries,
            "phi": phi, "d": DecryptionTable.getD(phi, E)}


def info():
    """Return the library version the page is running."""
    return {"version": npcryption.__version__}


ACTIONS = {
    "keys": keys,
    "encrypt": encrypt_steps,
    "decrypt": decrypt_steps,
    "crack": crack,
    "info": info,
}


def call(action, *args):
    """Run one of `ACTIONS` and return its result as a JSON string."""
    return json.dumps(ACTIONS[action](*args), ensure_ascii=False)
