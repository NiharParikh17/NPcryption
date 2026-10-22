from npcryption.core import Encryption
from npcryption.core import Decryption


def encrypt(P, Q, E, message):
    """Encrypt `message`; thin wrapper around `Encryption.encrypt`."""
    return Encryption.encrypt(P, Q, E, message)


def decrypt(P, Q, E, message):
    """Decrypt `message`; thin wrapper around `Decryption.decrypt`."""
    return Decryption.decrypt(P, Q, E, message)


def main():
    """Run the interactive prompt behind the `npcryption` command.

    Asks for E (encrypt) or D (decrypt), then P, Q, E and the message, and
    prints the result. Any other choice prints nothing.
    """
    answer = input("Press E for Encryption or D for Decryption: ")
    P = int(input("Enter Private Key P: "))
    Q = int(input("Enter Private Key Q: "))
    E = int(input("Enter Public Key E: "))

    if answer == "E" or answer == "e":
        message = input("Enter Message: ")
        print(encrypt(P, Q, E, message))

    elif answer == "D" or answer == "d":
        message = input("Encrypted Message: ")
        print(decrypt(P, Q, E, message))


if __name__ == "__main__":
    main()
