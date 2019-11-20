import math

class EncryptionTable:
    def __init__(self, n, validList):
        self.power: [int] = []
        self.prevSQR: [int] = []
        self.modNum: [int] = []
        self.validity: [bool] = []

        #Splitting into powers of 2
        highPow = EncryptionTable.getHighestPowerOf2(n)
        pow = 1 if n%2==1 else 2
        while (pow <= highPow):
            self.power.append(pow)
            self.prevSQR.append(0)
            self.modNum.append(0)
            val = True if pow in validList else False
            self.validity.append(val)
            pow *= 2

    def getHighestPowerOf2(n):
        return 2 ** int(math.log(n, 2))

    def setPrevSQR(self, value, index):
        self.prevSQR[index] = value

    def setModNum(self, value, index):
        self.modNum[index] = value

    def getProduct(self):
        product = 1
        for index in range(0, len(self.power)):
            if self.validity[index]:
                product *= self.modNum[index]
        return product

    def getLength(self):
        return len(self.power)