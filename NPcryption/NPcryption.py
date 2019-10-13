def getAscii(character):
    return ord(character)

def getValue(ascii):
    return chr(ascii);
          
def splitIntoValidMultiplesOf2(E, List): # This splits public key (E) into multiples of 2.
    LeftE = E
    while (int(LeftE) != 0):
        two = 1
        E = LeftE
        while (int(E) != 1):
            two = two * 2
            E = E//2
        LeftE = LeftE - two
        List.append(int(two))
    List.sort()
    
def splitIntoMultiplesOf2(E, List): # This creates multiples of 2 with max value of E and minimum 1.
        two = 1
        while (int(E) != 1):
            two = two*2
            E = E//2
        while (int(two) != 0):
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
        if (List[values][3] == "Y"):
            product = product*List[values][2]
    return product

def getD(P_Q, E): # This generates the value of D for decryption.
    ListOfD = [[P_Q, 1, 0, 0],[E, 0, 1, 0]] # Declaration of a list for finding D with formula (P-1)(Q-1)x + ED = 1 where first two entries are fixed
    nextR = P_Q%E
    rows = 1
    while (nextR != 1 and nextR != 0):
        rows = rows + 1
        nextR = ListOfD[rows-2][0]%ListOfD[rows-1][0]
        nextQ = ListOfD[rows-2][0]//ListOfD[rows-1][0]
        nextX = ListOfD[rows-2][1]-(ListOfD[rows-1][1]*nextQ)
        nextD = ListOfD[rows-2][2]-(ListOfD[rows-1][2]*nextQ)
        ListOfD.append([nextR, nextX, nextD, nextQ])
    D = (ListOfD[len(ListOfD)-1][2])
    if (D<0):
        D = D+P_Q
        return D
    else:
        return D
    
def main():
    answer = input("Press E for Encryption or D for Decryption: ")
    if (answer == "E" or answer == "e"): # This is code for encryption......
        message = input("Enter Message: ")
        P = int(input("Enter Private Key P: "))
        Q = int(input("Enter Private Key Q: "))
        E = int(input("Enter Public Key E: "))
        ValidMultiples = [] # Declaration of Empty Lists for Valid Multiples of 2
        Multiples = [] # Declaration of Empty Lists for Multiples of 2 which may contain invalid multiples too
        PQ = P*Q
        splitIntoMultiplesOf2(E, Multiples)
        splitIntoValidMultiplesOf2(E, ValidMultiples)
        for character in range (0, len(message)):
            ascii = getAscii(message[character])
            k = 0
            setPrevSQR(ascii, k, Multiples)
            modNum = ascii%PQ
            setModNum(modNum, k, Multiples)
            for multiple in range (0, len(Multiples)-1):
                k = k+1
                prevSQR = modNum*modNum
                setPrevSQR(prevSQR, k, Multiples)
                modNum = prevSQR%PQ
                setModNum(modNum, k, Multiples)
            createValidList(Multiples, ValidMultiples)
            product = getProduct(Multiples)
            EncryptedChar = product%PQ
            while(len(str(EncryptedChar)) != len(str(PQ))):
                EncryptedChar = "0"+str(EncryptedChar)
            print(EncryptedChar, end = "")
    
    elif (answer == "D" or answer == "d"): # This is code for decryption.....
        P = int(input("Enter Private Key P: "))
        Q = int(input("Enter Private Key Q: "))
        E = int(input("Enter Public Key E: "))
        PQ = P*Q
        D = getD((P-1)*(Q-1), E)
        Multiples = []
        ValidMultiples = []
        splitIntoMultiplesOf2(D, Multiples)
        splitIntoValidMultiplesOf2(D, ValidMultiples)
        createValidList(Multiples, ValidMultiples) 
        message = input("Encypted Message: ")
        CharLength = len(str(PQ))
        for eachCharCoded in range(0, len(message), CharLength):
            codedChar = int(message[eachCharCoded:eachCharCoded+CharLength])
            k = 0
            setPrevSQR(codedChar, k, Multiples)
            modNum = codedChar%PQ
            setModNum(modNum, k, Multiples)
            for mult in range(0, len(Multiples)-1):
                k = k+1
                prevSQR = modNum*modNum
                setPrevSQR(prevSQR, k, Multiples)
                modNum = prevSQR%PQ
                setModNum(modNum, k, Multiples)
            product = getProduct(Multiples)
            EncryptedSymbol = getValue(product%PQ)
            print(EncryptedSymbol, end = "")
            

main()


        
                       
