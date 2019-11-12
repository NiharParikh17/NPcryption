import math

def getAscii(character):
    return ord(character)


def getCharacter(ascii):
    return chr(ascii)


def splitIntoValidPowersOf2(E):
    validMultiples = []
    i = 1
    while i <= E:
        if i & E:
            validMultiples.append(i)
        i <<= 1
    return validMultiples

def getHighestPowerOf2(n):
    return 2 ** int(math.log(n, 2))

def splitIntoPowersOf2(E):
    multiples = []
    two = getHighestPowerOf2(E)
    while int(two) != 0:
        multiples.append([int(two), 0, 0, "N"])
        two = two // 2
    multiples.sort()
    return multiples


def setPrevSQR(prevSQR, K, List):
    List[K][1] = prevSQR


def setModNum(modNum, K, List):
    List[K][2] = modNum


def createValidList(List, List2):
    for x in range(0, len(List)):
        if List[x][0] in List2:
            List[x][3] = "Y"


def getProduct(List):
    product = 1
    for values in range(0, len(List)):
        if List[values][3] == "Y":
            product = product * List[values][2]
    return product


def getD(P_Q, E):
    ListOfD = [[P_Q, 1, 0, 0], [E, 0, 1, 0]]
    nextR = P_Q % E
    rows = 1
    while nextR != 1 and nextR != 0:
        rows = rows + 1
        nextR = ListOfD[rows - 2][0] % ListOfD[rows - 1][0]
        nextQ = ListOfD[rows - 2][0] // ListOfD[rows - 1][0]
        nextX = ListOfD[rows - 2][1] - (ListOfD[rows - 1][1] * nextQ)
        nextD = ListOfD[rows - 2][2] - (ListOfD[rows - 1][2] * nextQ)
        ListOfD.append([nextR, nextX, nextD, nextQ])
    D = (ListOfD[len(ListOfD) - 1][2])
    if D < 0:
        D = D + P_Q
        return D
    else:
        return D


def encrypt(P, Q, E, message):
    encyptedDict = {}
    encrypted_message = ""
    PQ = P * Q
    Multiples = splitIntoPowersOf2(E)
    ValidMultiples = splitIntoValidPowersOf2(E)
    createValidList(Multiples, ValidMultiples)
    for character in message:
        if character in encyptedDict:
            EncryptedChar = encyptedDict[character]
        else:
            EncryptedChar = encryptCharacter(PQ, character, Multiples);
            encyptedDict[character] = EncryptedChar
        encrypted_message = encrypted_message + EncryptedChar
    return encrypted_message

def encryptCharacter(PQ, character, Multiples):
    ascii = getAscii(character)
    k = 0
    setPrevSQR(ascii, k, Multiples)
    modNum = ascii % PQ
    setModNum(modNum, k, Multiples)
    for multiple in range(0, len(Multiples) - 1):
        k = k + 1
        prevSQR = modNum * modNum
        setPrevSQR(prevSQR, k, Multiples)
        modNum = prevSQR % PQ
        setModNum(modNum, k, Multiples)
    product = getProduct(Multiples)
    EncryptedChar = str(product % PQ)
    while len(str(EncryptedChar)) != len(str(PQ)):
        EncryptedChar = "0" + EncryptedChar
    return EncryptedChar


def decrypt(P, Q, E, message):
    decryptDict = {}
    plain_message = ""
    PQ = P * Q
    D = getD((P - 1) * (Q - 1), E)
    Multiples = splitIntoPowersOf2(D)
    ValidMultiples = splitIntoValidPowersOf2(D)
    createValidList(Multiples, ValidMultiples)
    CharLength = len(str(PQ))
    for eachCharCoded in range(0, len(message), CharLength):
        codedChar = int(message[eachCharCoded:eachCharCoded + CharLength])
        if codedChar in decryptDict:
            EncryptedSymbol = decryptDict[codedChar]
        else:
            EncryptedSymbol = decryptCharacter(PQ, codedChar, Multiples)
            decryptDict[codedChar] = EncryptedSymbol
        plain_message = plain_message + EncryptedSymbol
    return plain_message

def decryptCharacter(PQ, codedChar, Multiples):
    k = 0
    setPrevSQR(codedChar, k, Multiples)
    modNum = codedChar % PQ
    setModNum(modNum, k, Multiples)
    for mult in range(0, len(Multiples) - 1):
        k = k + 1
        prevSQR = modNum * modNum
        setPrevSQR(prevSQR, k, Multiples)
        modNum = prevSQR % PQ
        setModNum(modNum, k, Multiples)
    product = getProduct(Multiples)
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
