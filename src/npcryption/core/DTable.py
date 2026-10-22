class DTable:
    """Extended Euclidean Algorithm table that finds the RSA private exponent D.

    The lists are the table's columns: `R` remainders, `Q` quotients, and
    `X` / `D` the Bezout coefficients of `PQ` and `E`. Note that `PQ` here is
    the totient phi(N) = (P - 1) * (Q - 1), not P * Q.
    """

    def __init__(self, PQ, E):
        """Seed the first two rows of the table with `PQ` (phi(N)) and `E`."""
        self.R: [] = [PQ, E]
        self.X: [] = [1, 0]
        self.D: [] = [0, 1]
        self.Q: [] = [0, 0]

    def generateTable(self):
        """Add rows until the remainder reaches 1, or 0 if `E` is not coprime with `PQ`.

        Call it once per instance; a second call appends duplicate rows.
        """
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
        """Return D from the last row, made non-negative by adding `PQ` if needed."""
        D = (self.D[len(self.D) - 1])
        if D < 0:
            D = D + PQ
        return D
