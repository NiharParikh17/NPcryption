from .EncryptionTable import EncryptionTable


def getAscii(character):
    """Return the code point of a single character (`ord`)."""
    return ord(character)


def getCharacter(ascii):
    """Return the character for a code point (`chr`). Not used by `encrypt`."""
    return chr(ascii)


def encrypt(P, Q, E, message):
    """Encrypt `message` with the RSA key (P, Q, E) and return the ciphertext.

    Each character becomes `ord(character) ** E % (P * Q)`, left-padded with
    zeros to `len(str(P * Q))` digits, and the blocks are concatenated.
    Every character's code point must be below P * Q for `decrypt` to recover
    it. The key is not validated.
    """
    encyptedDict = {}
    encrypted_message = ""
    PQ = P * Q
    powers = EncryptionTable(E)
    for character in message:
        if character in encyptedDict:
            EncryptedChar = encyptedDict[character]
        else:
            EncryptedChar = encryptCharacter(PQ, character, powers)
            encyptedDict[character] = EncryptedChar
        encrypted_message = encrypted_message + EncryptedChar
    return encrypted_message


def encryptCharacter(PQ, character, powers):
    """Encrypt one character and return its zero-padded cipher block.

    `PQ` is the modulus N = P * Q and `powers` is an `EncryptionTable` for
    exponent E; its rows are overwritten on every call.
    """
    ascii = getAscii(character)
    k = 0
    powers.set_prev_sqr(ascii, k)
    modNum = ascii % PQ
    powers.set_mod_num(modNum, k)
    for x in range(0, powers.get_length() - 1):
        k = k + 1
        prevSQR = modNum * modNum
        powers.set_prev_sqr(prevSQR, k)
        modNum = prevSQR % PQ
        powers.set_mod_num(modNum, k)
    product = powers.get_product()
    EncryptedChar = str(product % PQ)
    while len(str(EncryptedChar)) != len(str(PQ)):
        EncryptedChar = "0" + EncryptedChar
    return EncryptedChar
