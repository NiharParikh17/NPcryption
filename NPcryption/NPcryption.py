import Encryption
import Decryption
import tkinter as tk

def encrypt(P, Q, E, message):
    """Encrypting the message by calling encrypt function in Encryption"""
    return Encryption.encrypt(P, Q, E, message)

def decrypt(P, Q, E, message):
    """Decrypting the message by calling decrypt function in Decryption"""
    return Decryption.decrypt(P, Q, E, message)

def buildGUI():
    window = tk.Tk()
    label = tk.Label(
        text="NPcryption",
        foreground="red"
    )
    label.pack()
    window.mainloop()

def main():
    print("GUI in progress!")
    buildGUI()

main()