import uuid
import Client
import tkinter as tk
import GUI as guipy

MAC_ADDR = hex(uuid.getnode())

if __name__ == "__main__":
    gui = tk.Tk()
    gui.title("Client DHCP")
    GUI = guipy.GUI(gui)
    gui.mainloop()
    client = Client.Client(MAC_ADDR, 68)
    client.discover()
    client.listen_broadcast()
    client.request()