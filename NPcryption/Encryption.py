from EncryptionTable import EncryptionTable

def getAscii(character):
    return ord(character)

def getCharacter(ascii):
    return chr(ascii)

def encrypt(P, Q, E, message):
    encyptedDict = {}
    encrypted_message = ""
    PQ = P * Q
    powers = EncryptionTable(E)
    for character in message:
        if character in encyptedDict:
            EncryptedChar = encyptedDict[character]
        else:
            EncryptedChar = encryptCharacter(PQ, character, powers);
            encyptedDict[character] = EncryptedChar
        encrypted_message = encrypted_message + EncryptedChar
    return encrypted_message

def encryptCharacter(PQ, character, powers):
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
