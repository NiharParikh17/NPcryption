def getAscii(character):
    return ord(character)

def getValue(ascii):
    return chr(ascii)

def splitIntoValidMultiplesOf2(E, List):
    LeftE = E
    while int(LeftE) != 0:
        two = 1
        E = LeftE
        while int(E) != 1:
            two = two * 2
            E = E//2
        LeftE = LeftE - two
        List.append(int(two))
    List.sort()

def splitIntoMultiplesOf2(E, List):
        two = 1
        while int(E) != 1:
            two = two*2
            E = E//2
        while int(two) != 0:
            List.append([int(two), 0, 0, "N"])
            two = two//2
        List.sort()

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
    for values in range (0, len(List)):
        if List[values][3] == "Y":
            product = product*List[values][2]
    return product

def getD(P_Q, E):
    ListOfD = [[P_Q, 1, 0, 0],[E, 0, 1, 0]]
    nextR = P_Q % E
    rows = 1
    while nextR != 1 and nextR != 0:
        rows = rows + 1
        nextR = ListOfD[rows-2][0]%ListOfD[rows-1][0]
        nextQ = ListOfD[rows-2][0]//ListOfD[rows-1][0]
        nextX = ListOfD[rows-2][1]-(ListOfD[rows-1][1]*nextQ)
        nextD = ListOfD[rows-2][2]-(ListOfD[rows-1][2]*nextQ)
        ListOfD.append([nextR, nextX, nextD, nextQ])
    D = (ListOfD[len(ListOfD)-1][2])
    if D < 0:
        D = D + P_Q
        return D
    else:
        return D

def encrypt(P, Q, E, message):
    PQ = P*Q
    ValidMultiples = []
    Multiples = []
    splitIntoMultiplesOf2(E, Multiples)
    splitIntoValidMultiplesOf2(E, ValidMultiples)
    for character in range(0, len(message)):
        ascii = getAscii(message[character])
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
        createValidList(Multiples, ValidMultiples)
        product = getProduct(Multiples)
        EncryptedChar = product % PQ
        while len(str(EncryptedChar)) != len(str(PQ)):
            EncryptedChar = "0" + str(EncryptedChar)
        print(EncryptedChar, end="")

def decrypt(P, Q, E, message):
    PQ = P*Q
    ValidMultiples = []
    Multiples = []
    D = getD((P - 1) * (Q - 1), E)
    splitIntoMultiplesOf2(D, Multiples)
    splitIntoValidMultiplesOf2(D, ValidMultiples)
    createValidList(Multiples, ValidMultiples)
    CharLength = len(str(PQ))
    for eachCharCoded in range(0, len(message), CharLength):
        codedChar = int(message[eachCharCoded:eachCharCoded + CharLength])
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
        EncryptedSymbol = getValue(product % PQ)
        print(EncryptedSymbol, end="")

def main():
    answer = input("Press E for Encryption or D for Decryption: ")
    P = int(input("Enter Private Key P: "))
    Q = int(input("Enter Private Key Q: "))
    E = int(input("Enter Public Key E: "))

    if answer == "E" or answer == "e":
        message = input("Enter Message: ")
        encrypt(P, Q, E, message)

    elif answer == "D" or answer == "d":
        message = input("Encrypted Message: ")
        decrypt(P, Q, E, message)

main()