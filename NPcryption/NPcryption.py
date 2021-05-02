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

    #Heading
    frame_heading = tk.Frame()
    label = tk.Label(
        master=frame_heading,
        text="NPcryption",
        foreground="red"
    )
    label.pack()

    #P input
    frame_P_input = tk.Frame()
    P_label = tk.Label(
        master=frame_P_input,
        text="P:",
        foreground="black"
    )
    P_entry = tk.Entry(
        master=frame_P_input,
        fg="black",
        bg="white",
        width=50
    )
    P_label.pack(side=tk.LEFT, padx=5, pady=5)
    P_entry.pack(fill=tk.X, padx=5)

    #Q input
    frame_Q_input = tk.Frame()
    Q_label = tk.Label(
        master=frame_Q_input,
        text="Q:",
        foreground="black"
    )
    Q_entry = tk.Entry(
        master=frame_Q_input,
        fg="black",
        bg="white",
        width=50
    )
    Q_label.pack(side=tk.LEFT, padx=5, pady=5)
    Q_entry.pack(fill=tk.X, padx=5)

    #E input
    frame_E_input = tk.Frame()
    E_label = tk.Label(
        master=frame_E_input,
        text="E:",
        foreground="black"
    )
    E_entry = tk.Entry(
        master=frame_E_input,
        fg="black",
        bg="white",
        width=50
    )
    E_label.pack(side=tk.LEFT, padx=5, pady=5)
    E_entry.pack(fill=tk.X, padx=5)

    #Packing the frames
    frame_heading.pack()
    frame_P_input.pack()
    frame_Q_input.pack()
    frame_E_input.pack()

    window.mainloop()

def main():
    print("GUI in progress!")
    buildGUI()

main()