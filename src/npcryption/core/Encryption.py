from EncryptionTable import EncryptionTable


def getAscii(character):
    """Get the ascii value of the character"""
    return ord(character)


def getCharacter(ascii):
    """Get the character of the ascii value"""
    return chr(ascii)


def encrypt(P, Q, E, message):
    """Encrypting the given message using P, Q, and E"""
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
    """Encrypting a single given character"""
    ascii = getAscii(character)
    k = 0
    powers.setPrevSQR(ascii, k)
    modNum = ascii % PQ
    powers.setModNum(modNum, k)
    for x in range(0, powers.getLength() - 1):
        k = k + 1
        prevSQR = modNum * modNum
        powers.setPrevSQR(prevSQR, k)
        modNum = prevSQR % PQ
        powers.setModNum(modNum, k)
    product = powers.getProduct()
    EncryptedChar = str(product % PQ)
    while len(str(EncryptedChar)) != len(str(PQ)):
        EncryptedChar = "0" + EncryptedChar
    return EncryptedChar
