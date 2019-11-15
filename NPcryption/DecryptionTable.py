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