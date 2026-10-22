from .EncryptionTable import EncryptionTable
from .DTable import DTable


class DecryptionTable(EncryptionTable):
    """`EncryptionTable` built for the private exponent D instead of E.

    Note that `PQ` here is the totient phi(N) = (P - 1) * (Q - 1), not P * Q.
    """

    def __init__(self, PQ, E):
        """Derive D from `PQ` (phi(N)) and `E`, then build the table for D."""
        d = DecryptionTable.getD(PQ, E)
        super().__init__(d)

    def getD(P_Q, E):
        """Return D, the inverse of `E` modulo `P_Q` (phi(N)), using `DTable`.

        Not a staticmethod: call it on the class, `DecryptionTable.getD(phi, E)`.
        """
        decryptT = DTable(P_Q, E)
        decryptT.generateTable()
        return decryptT.getD(P_Q)
