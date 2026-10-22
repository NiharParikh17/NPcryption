import math


def split_into_valid_powers_of_2(n):
    """Return the powers of 2 that sum to `n` (its set bits), smallest first.

    Example: `split_into_valid_powers_of_2(13) == [1, 4, 8]`.
    """
    validMultiples = []
    i = 1
    while i <= n:
        if i & n:
            validMultiples.append(i)
        i <<= 1
    return validMultiples


def get_highest_power_of_2(n):
    """Return the largest power of 2 that is <= `n` (`n` must be positive)."""
    return 2 ** int(math.log(n, 2))


class EncryptionTable:
    """Square-and-multiply table used to compute `M ** n % N` for exponent `n`.

    Row k holds `M ** (2 ** k) % N` in `modNum`, filled in by the caller
    (see `encryptCharacter`). `validity[k]` marks the rows whose power of 2
    is a set bit of `n`, and `get_product` multiplies those rows together.
    Results are only correct for odd `n`, which always holds for RSA
    exponents.
    """

    def __init__(self, n):
        """Create an empty table for exponent `n`."""
        self.power: [int] = []
        self.prevSQR: [int] = []
        self.modNum: [int] = []
        self.validity: [bool] = []
        self.initialize(n)

    def initialize(self, n):
        """Add one zeroed row per power of 2 up to `n`, marking the rows `n` uses."""
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
        """Record row `index` before reducing modulo N (kept for inspection only)."""
        self.prevSQR[index] = value

    def set_mod_num(self, value, index):
        """Store row `index` reduced modulo N; this is what `get_product` uses."""
        self.modNum[index] = value

    def get_product(self):
        """Return the product of the valid `modNum` rows, not reduced modulo N."""
        product = 1
        for index in range(0, len(self.power)):
            if self.validity[index]:
                product *= self.modNum[index]
        return product

    def get_length(self):
        """Return the number of rows, i.e. how many values the caller must fill in."""
        return len(self.power)
