from DTable import DTable
from EncryptionTable import EncryptionTable

def getAscii(character):
    return ord(character)

def getCharacter(ascii):
    return chr(ascii)

def getD(P_Q, E):
    decryptT = DTable(P_Q, E)
    decryptT.generateTable()
    return decryptT.getD(P_Q)

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

def decrypt(P, Q, E, message):
    decryptDict = {}
    plain_message = ""
    PQ = P * Q
    D = getD((P - 1) * (Q - 1), E)
    powers = EncryptionTable(D)
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
    k = 0
    powers.setPrevSQR(codedChar, k)
    modNum = codedChar % PQ
    powers.setModNum(modNum, k)
    for x in range(0, powers.getLength() - 1):
        k = k + 1
        prevSQR = modNum * modNum
        powers.setPrevSQR(prevSQR, k)
        modNum = prevSQR % PQ
        powers.setModNum(modNum, k)
    product = powers.getProduct()
    EncryptedSymbol = getCharacter(product % PQ)
    return EncryptedSymbol

def main():
    answer = input("Press E for Encryption or D for Decryption: ")
    P = int(input("Enter Private Key P: "))
    Q = int(input("Enter Private Key Q: "))
    E = int(input("Enter Public Key E: "))

    if answer == "E" or answer == "e":
        message = input("Enter Message: ")
        print(encrypt(P, Q, E, message))

    elif answer == "D" or answer == "d":
        message = input("Encrypted Message: ")
        print(decrypt(P, Q, E, message))

main()