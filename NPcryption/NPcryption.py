import Encryption
import Decryption
import tkinter as tk

def encrypt(P, Q, E, message):
    """Encrypting the message by calling encrypt function in Encryption"""
    return Encryption.encrypt(P, Q, E, message)

def decrypt(P, Q, E, message):
    """Decrypting the message by calling decrypt function in Decryption"""
    return Decryption.decrypt(P, Q, E, message)

def main():
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

main()