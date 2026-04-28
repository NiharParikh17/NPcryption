import math


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


class EncryptionTable:
    def __init__(self, n):
        self.power: [int] = []
        self.prevSQR: [int] = []
        self.modNum: [int] = []
        self.validity: [bool] = []
        self.initialize(n)

    def initialize(self, n):
        validList = splitIntoValidPowersOf2(n)
        highPow = getHighestPowerOf2(n)
        pow = 1 if n % 2 == 1 else 2
        while pow <= highPow:
            self.power.append(pow)
            self.prevSQR.append(0)
            self.modNum.append(0)
            val = True if pow in validList else False
            self.validity.append(val)
            pow *= 2

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
