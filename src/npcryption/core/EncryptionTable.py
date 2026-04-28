import math


def split_into_valid_powers_of_2(n):
    validMultiples = []
    i = 1
    while i <= n:
        if i & n:
            validMultiples.append(i)
        i <<= 1
    return validMultiples


def get_highest_power_of_2(n):
    return 2 ** int(math.log(n, 2))


class EncryptionTable:
    def __init__(self, n):
        self.power: [int] = []
        self.prevSQR: [int] = []
        self.modNum: [int] = []
        self.validity: [bool] = []
        self.initialize(n)

    def initialize(self, n):
        validList = split_into_valid_powers_of_2(n)
        highPow = get_highest_power_of_2(n)
        pow = 1 if n % 2 == 1 else 2
        while pow <= highPow:
            self.power.append(pow)
            self.prevSQR.append(0)
            self.modNum.append(0)
            val = True if pow in validList else False
            self.validity.append(val)
            pow *= 2

    def set_prev_sqr(self, value, index):
        self.prevSQR[index] = value

    def set_mod_num(self, value, index):
        self.modNum[index] = value

    def get_product(self):
        product = 1
        for index in range(0, len(self.power)):
            if self.validity[index]:
                product *= self.modNum[index]
        return product

    def get_length(self):
        return len(self.power)
