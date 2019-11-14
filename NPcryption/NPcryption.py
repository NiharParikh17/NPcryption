import math

class DecryptionTable:
    def __init__(self, PQ, E):
        self.R: [] = [PQ, E]
        self.X: [] = [1, 0]
        self.D: [] = [0, 1]
        self.Q: [] = [0, 0]

    def generateTable(self):
        currentRow = 2
        nextR = None
        while nextR != 1 and nextR != 0:
            nextR = self.R[currentRow - 2] % self.R[currentRow - 1]
            self.R.append(nextR)
            nextQ = self.R[currentRow - 2] // self.R[currentRow - 1]
            self.Q.append(nextQ)
            self.X.append(self.X[currentRow - 2] - (self.X[currentRow - 1] * nextQ))
            self.D.append(self.D[currentRow - 2] - (self.D[currentRow - 1] * nextQ))
            currentRow += 1

    def getD(self, PQ):
        D = (self.D[len(self.D) - 1])
        if D < 0: D = D + PQ
        return D

def getAscii(character):
    return ord(character)

def getCharacter(ascii):
    return chr(ascii)

def splitIntoValidPowersOf2(n):
    validMultiples = []
    i = 1
    while i <= n:
        if i & n:
            validMultiples.append(i)
        i <<= 1
    return validMultiples

def getHighestPowerOf2(n):
    return 2 ** int(math.log(n, 2))

def splitIntoPowersOf2(n):
    multiples = []
    two = getHighestPowerOf2(n)
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
    decryptT = DecryptionTable(P_Q, E)
    decryptT.generateTable()
    return decryptT.getD(P_Q)

def encrypt(P, Q, E, message):
    encyptedDict = {}
    encrypted_message = ""
    PQ = P * Q
    multiples = splitIntoPowersOf2(E)
    validMultiples = splitIntoValidPowersOf2(E)
    createValidList(multiples, validMultiples)
    for character in message:
        if character in encyptedDict:
            EncryptedChar = encyptedDict[character]
        else:
            EncryptedChar = encryptCharacter(PQ, character, multiples);
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
    multiples = splitIntoPowersOf2(D)
    validMultiples = splitIntoValidPowersOf2(D)
    createValidList(multiples, validMultiples)
    CharLength = len(str(PQ))
    for eachCharCoded in range(0, len(message), CharLength):
        codedChar = int(message[eachCharCoded:eachCharCoded + CharLength])
        if codedChar in decryptDict:
            EncryptedSymbol = decryptDict[codedChar]
        else:
            EncryptedSymbol = decryptCharacter(PQ, codedChar, multiples)
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