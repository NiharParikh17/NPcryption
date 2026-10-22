from .DecryptionTable import DecryptionTable


def getAscii(character):
    """Return the code point of a single character (`ord`). Not used by `decrypt`."""
    return ord(character)


def getCharacter(ascii):
    """Return the character for a code point (`chr`)."""
    return chr(ascii)


def decrypt(P, Q, E, message):
    """Decrypt a ciphertext produced by `encrypt` with the same (P, Q, E).

    `message` is split into blocks of `len(str(P * Q))` digits. Each block
    is raised to the private exponent D (derived from E) modulo P * Q and
    turned back into a character. `message` must contain only digits.
    """
    decryptDict = {}
    plain_message = ""
    PQ = P * Q
    powers = DecryptionTable((P - 1) * (Q - 1), E)
    CharLength = len(str(PQ))
    for eachCharCoded in range(0, len(message), CharLength):
        codedChar = int(message[eachCharCoded:eachCharCoded + CharLength])
        if codedChar in decryptDict:
            EncryptedSymbol = decryptDict[codedChar]
        else:
            EncryptedSymbol = decryptCharacter(PQ, codedChar, powers)
            decryptDict[codedChar] = EncryptedSymbol
        plain_message = plain_message + EncryptedSymbol
    return plain_message


def decryptCharacter(PQ, codedChar, powers):
    """Decrypt one cipher block, given as an int, and return the character.

    `PQ` is the modulus N = P * Q and `powers` is a `DecryptionTable` for
    the private exponent D; its rows are overwritten on every call.
    """
    k = 0
    powers.set_prev_sqr(codedChar, k)
    modNum = codedChar % PQ
    powers.set_mod_num(modNum, k)
    for x in range(0, powers.get_length() - 1):
        k = k + 1
        prevSQR = modNum * modNum
        powers.set_prev_sqr(prevSQR, k)
        modNum = prevSQR % PQ
        powers.set_mod_num(modNum, k)
    product = powers.get_product()
    EncryptedSymbol = getCharacter(product % PQ)
    return EncryptedSymbol
