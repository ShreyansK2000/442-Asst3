import server
import client
import sys
from tkinter import *
import gui

root = Tk()
root.title("Team TBD's VPN")
isServerApp = BooleanVar()

def launch():
    global isServerApp, root
    root.destroy()

    if isServerApp.get():
        server.do_server()
    else: 
        
    server.do_server() if isServerApp.get() else client.establish_connection()

if __name__ == "__main__":
      
  
    frame1 = Frame(root)
    frame1.pack()
    
    label1 = Label(frame1, text="Client or Server app?")
    label1.pack()

    radio1 = Radiobutton(frame1, text="Client", variable=isServerApp, value=False)
    radio1.pack()

    radio2 = Radiobutton(frame1, text="Server", variable=isServerApp, value=True)
    radio2.pack()

    button1 = Button(frame1, text="Select", command=launch)
    button1.pack()

    root.mainloop()

