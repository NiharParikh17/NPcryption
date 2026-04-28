from .DecryptionTable import DecryptionTable


def getAscii(character):
    """Get the ascii value of the character"""
    return ord(character)


def getCharacter(ascii):
    """Get the character of the ascii value"""
    return chr(ascii)


def decrypt(P, Q, E, message):
    """Decrypting the given message using P, Q, and E"""
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
    """Decrypting a single given character"""
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
