import tkinter as tk
import server
import client

LARGE_FONT = ("Verdana", 12)


class VPN(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.title('VPN')
        self.geometry("400x200")

        # The container - parent frame
        container = tk.Frame(self)
        container.grid()  # pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # List of child frame - client and server
        self.frames = {}

        c_frame = ClientPage(container, self)
        s_frame = ServerPage(container, self)
        self.frames["Client"] = c_frame
        self.frames["Server"] = s_frame

        c_frame.grid(row=0, column=0, sticky="nsew")
        s_frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Client")

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


# Client mode, the program can initiate a TCP connection
# to a given IP address, on a given port ;
# input: IP address, on a given port, Shared Secret Value, Data to be Sent
class ClientPage(tk.Frame):

    def __init__(self, parent, controller):

        # Stored variables for client

        # ____________________________

        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text="Client Mode", font=LARGE_FONT)
        self.label.grid(row=0, column=0)

        label1 = tk.Label(self, text="IP Address")
        label2 = tk.Label(self, text="Port #")
        label3 = tk.Label(self, text="Shared Secret Value")
        #label4 = tk.Label(self, text="Data to be sent")
        self.entries = {}
        entry1 = tk.Entry(self)
        entry2 = tk.Entry(self)
        entry3 = tk.Entry(self)
        #entry4 = tk.Entry(self)

        self.entries[0] = entry1
        self.entries[1] = entry2
        self.entries[2] = entry3
        #self.entries[3] = entry4

        label1.grid(row=1, column=0)
        label2.grid(row=2, column=0)
        label3.grid(row=3, column=0)
        #label4.grid(row=4, column=0)

        entry1.grid(row=1, column=1)
        entry2.grid(row=2, column=1)
        entry3.grid(row=3, column=1)
        #entry4.grid(row=4, column=1)

        #label.grid(pady=10, padx=10)

        switch_button = tk.Button(self, text="Server",
                                  command=lambda: controller.show_frame("Server"))
        switch_button.grid(row=5, column=0)

        self.proceed_button = tk.Button(
            self, text="Continue", command=self.connect)
        self.proceed_button.grid(row=5, column=1)
        close_button = tk.Button(self, text="Close",
                                 command=controller.quit)
        close_button.grid(row=5, column=2)

    def connect(self):
        self.IP_adr = self.entries[0].get()
        self.port = self.entries[1].get()
        self.secret_value = self.entries[2].get()
        print(self.secret_value)
        connected = 1
        # Call the do_client function
        # connected = client.do_client()

        if(connected):
            print("HERE")
            label4 = tk.Label(self, text="Data to be sent")
            entry4 = tk.Entry(self)
            self.entries[3] = entry4
            label4.grid(row=4, column=0)
            entry4.grid(row=4, column=1)
            self.label.config(text="Client Mode - Connected")
            self.proceed_button.config(text="Send")

        return connected


class ServerPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Stored variables for server

        # ____________________________

        label = tk.Label(self, text="Server Mode", font=LARGE_FONT)
        label.grid(pady=10, padx=10)

        switch_button = tk.Button(self, text="Client",
                                  command=lambda: controller.show_frame("Client"))
        switch_button.grid(row=1, column=0)
        close_button = tk.Button(self, text="Close",
                                 command=controller.quit)
        close_button.grid(row=1, column=1)


app = VPN()
app.mainloop()
