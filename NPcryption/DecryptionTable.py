from EncryptionTable import EncryptionTable
from DTable import DTable


class DecryptionTable(EncryptionTable):
    def __init__(self, PQ, E):
        d = DecryptionTable.getD(PQ, E)
        super().__init__(d)

    def getD(P_Q, E):
        decryptT = DTable(P_Q, E)
        decryptT.generateTable()
        return decryptT.getD(P_Q)
