import tkinter as tk
from tkinter import ttk
from client import Client
from server import Server
from comm_constants import *
import time
import threading

LARGE_FONT = ("Verdana", 12)


class VPN(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.title('VPN')
        self.geometry("400x200")

        # The container - parent frame
        container = ttk.Notebook(self)
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

        container.add(c_frame, text="CLIENT")
        container.add(s_frame, text="SERVER")

        self.show_frame("Client")

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# Client mode, the program can initiate a TCP connection
# to a given IP address, on a given port ;
# input: IP address, on a given port, Shared Secret Value, Data to be Sent


class ClientPage(tk.Frame):

    def __init__(self, parent, controller):\
        
        #Initialize a client object
        self.client = Client()

        tk.Frame.__init__(self, parent)

        self.step_num = 0

        self.label = tk.Label(self, text="Client Mode", font=LARGE_FONT)
        self.label.grid(row=0, column=0)

        # ____________________Input____________________________________
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
        self.labeldata1 = tk.Label(self, text="Data Exchanged")
        self.labeldata1.grid(row=1, column=2)
        self.labeldata2 = tk.Label(self, text="")
        self.labeldata2.grid(row=2, column=2)

        # ________________Controll buttons______________________________
        # switch_button = tk.Button(self, text="Server",
        #                           command=lambda: controller.show_frame("Server"))
        # switch_button.grid(row=6, column=0)

        self.continue_button = tk.Button(
            self, text="Continue", command=self.step)
        self.continue_button.grid(row=6, column=0)
        self.connect_button = tk.Button(
            self, text="Connect", command=self.connect)
        self.connect_button.grid(row=6, column=1)
        close_button = tk.Button(self, text="Close",
                                 command=controller.quit)
        close_button.grid(row=6, column=2)

    # This function reads input from users,
    # call the authentication function from client
    # Update if client - server is connected
    def connect(self):
        self.ip_adr = self.entries[0].get()
        self.port = self.entries[1].get()
        self.secret_value = self.entries[2].get()
        

        # length = len(self.secret_value)
        # if(length < 32):
        #     for i in range(length, 32):
        #         self.secret_value += '0'
        # elif length > 32:
        #     self.secret_value = self.secret_value[0:32]

        # Call the do_client function
        
        self.client.establish_connection(
            self.ip_adr,
            self.port,
            self.secret_value,
        )
        self.status, message = self.client.execute()
        # self.status, message = self.client.establish_connection(self.ip_adr, self.port, self.secret_value)

        label4 = tk.Label(self, text="")
        label4.grid(row=4, column=0)
        if(self.status == OK_AUTHENTICATED):
            for entrytuple in self.entries.items():
                entrytuple[1].config(state="disabled")
            #label4 = tk.Label(self, text="Data to be sent")
            label4.config(text="Data to be sent")
            entry4 = tk.Entry(self)
            self.entries[3] = entry4
            #label4.grid(row=4, column=0)
            entry4.grid(row=4, column=1)
            recvThread = threading.Thread(target=self.recv)
            recvThread.setDaemon(True)
            recvThread.start()
            self.label.config(text="Client Mode - Connected")
            self.connect_button.config(text="Send", command=self.send)
            self.labeldata2.config(text = message)
        else:
            # TODO use another label to write the error message
            self.label.config(text="Client Mode - No Connection")
            label4.config(text=message)

    # Continue button function
    def step(self):
        if self.step_num == 0:
            print("Client Step number: ",self.step_num)
            self.ip_adr = self.entries[0].get()
            self.port = self.entries[1].get()
            self.secret_value = self.entries[2].get()
            self.client.establish_connection(
                self.ip_adr,
                self.port,
                self.secret_value,
            )
            self.step_num += 1
        elif self.step_num <= 3:
            print("Client Step number: ",self.step_num)
            self.status, message = self.client.execute(True,self.step_num )
            print('message', message)
            self.labeldata2.config(text = message)
            self.step_num += 1
        
        if self.step_num ==4:
            print("Client Step number: ",self.step_num)
            label4 = tk.Label(self, text="")
            label4.grid(row=4, column=0)
            if(self.status == OK_AUTHENTICATED):
                for entrytuple in self.entries.items():
                    entrytuple[1].config(state="disabled")
                #label4 = tk.Label(self, text="Data to be sent")
                label4.config(text="Data to be sent")
                entry4 = tk.Entry(self)
                self.entries[3] = entry4
                #label4.grid(row=4, column=0)
                entry4.grid(row=4, column=1)
                recvThread = threading.Thread(target=self.recv)
                recvThread.setDaemon(True)
                recvThread.start()
                self.label.config(text="Client Mode - Connected")
                self.connect_button.config(text="Send", command=self.send)
            else:
                # TODO use another label to write the error message
                self.label.config(text="Client Mode - No Connection")
                label4.config(text=message)
            

    # This function is used to send input data
    # once the authentication finishes
    def send(self):
        self.data_to_send = self.entries[3].get()
        status, cipher = self.client.send_data(self.data_to_send)
        self.labeldata2.config(text = cipher)
        # TODO update GUI telling that data sent

    def recv(self):
        label5 = tk.Label(self, text="Data received")
        label5.grid(row=5, column=0)
        label6 = tk.Label(self, text="No data")
        label6.grid(row=5, column=1)
        while True:
            # received_val = self.client.receive_data()
            # # print(received_val)
            # # TODO update GUI label with received_val
            # label6.config(text=str(received_val))

            status, received_val, cipher = self.client.receive_data()
            if status is OK_RECEIVED_MESSAGE:
                label6.config(text=str(received_val))
                self.labeldata2.config(text = cipher)
            else:
                # TODO do a popup connection closed
                # in this case go back to the main server menu
                pass


class ServerPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        #Initialize a client object
        self.server = Server()

        self.step_num = 0

        self.label = tk.Label(self, text="Server Mode", font=LARGE_FONT)
        self.label.grid(pady=10, padx=10)

        # ____________________Input____________________________________
        label1 = tk.Label(self, text="Port #")
        label2 = tk.Label(self, text="Shared Secret Value")
        self.entries = {}
        entry1 = tk.Entry(self)
        entry2 = tk.Entry(self)
        self.entries[0] = entry1
        self.entries[1] = entry2

        label1.grid(row=1, column=0)
        label2.grid(row=2, column=0)
        entry1.grid(row=1, column=1)
        entry2.grid(row=2, column=1)

        self.labeldata1 = tk.Label(self, text="Data Exchanged")
        self.labeldata1.grid(row=1, column=2)
        self.labeldata2 = tk.Label(self, text="")
        self.labeldata2.grid(row=2, column=2)

        # ________________Controll buttons______________________________
        # switch_button = tk.Button(self, text="Client",
        #                           command=lambda: controller.show_frame("Client"))
        # switch_button.grid(row=5, column=0)
        self.step_button = tk.Button(
            self, text="Continue", command=self.step)
        self.step_button.grid(row=5, column=0)
        self.connect_button = tk.Button(
            self, text="Start", command=self.connect)
        self.connect_button.grid(row=5, column=1)
        close_button = tk.Button(self, text="Close", command=controller.quit)
        close_button.grid(row=5, column=2)

    def connect(self):
        self.port = self.entries[0].get()
        self.secret_value = self.entries[1].get()

        # length = len(self.secret_value)
        # if(length < 32):
        #     for i in range(length, 32):
        #         self.secret_value += '0'
        # elif length > 32:
        #     self.secret_value = self.secret_value[0:32]

        # self.server = Server()
        self.server.listen_connections(
            self.port,
            self.secret_value
        )
        self.status, message = self.server.execute()

        label3 = tk.Label(self, text="")
        label3.grid(row=3, column=0)
        if(self.status == OK_AUTHENTICATED):
            print("HERE server")
            for entrytuple in self.entries.items():
                entrytuple[1].config(state="disabled")
            #label4 = tk.Label(self, text="Data to be sent")
            label3.config(text="Data to be sent")
            entry3 = tk.Entry(self)
            self.entries[2] = entry3
            #label4.grid(row=4, column=0)
            entry3.grid(row=3, column=1)
            recvThread = threading.Thread(target=self.recv)
            recvThread.setDaemon(True)
            recvThread.start()
            self.label.config(text="Server Mode - Connected")
            self.connect_button.config(text="Send", command=self.send)
        else:
            # TODO use another label to write the error message
            self.label.config(text="Server Mode - No Connection")
            label3.config(text=message)

    def step(self):
        if self.step_num == 0:
            print("Server Step number: ",self.step_num)
            self.port = self.entries[0].get()
            self.secret_value = self.entries[1].get()

            self.server.listen_connections(
                self.port,
                self.secret_value
            )
            self.step_num += 1
        elif self.step_num <= 3:
            print("Server Step number: ",self.step_num)
            self.status, message = self.server.execute(True,self.step_num )
            print(message)
            self.labeldata2.config(text = message)
            self.step_num += 1
        if self.step_num == 4: 
            print("Server Step number: ",self.step_num)
            label3 = tk.Label(self, text="")
            label3.grid(row=3, column=0)
            if(self.status == OK_AUTHENTICATED):
                print("HERE server")
                for entrytuple in self.entries.items():
                    entrytuple[1].config(state="disabled")
                #label4 = tk.Label(self, text="Data to be sent")
                label3.config(text="Data to be sent")
                entry3 = tk.Entry(self)
                self.entries[2] = entry3
                #label4.grid(row=4, column=0)
                entry3.grid(row=3, column=1)
                recvThread = threading.Thread(target=self.recv)
                recvThread.setDaemon(True)
                recvThread.start()
                self.label.config(text="Server Mode - Connected")
                self.connect_button.config(text="Send", command=self.send)
            else:
                # TODO use another label to write the error message
                self.label.config(text="Server Mode - No Connection")
                label3.config(text=message)

    def send(self):
        self.data_to_send = self.entries[2].get()
        status, cipher = self.server.send_data(self.data_to_send)
        self.labeldata2.config(text = cipher)
        # TODO update GUI telling that data sent

    def recv(self):
        label4 = tk.Label(self, text="Data received")
        label4.grid(row=4, column=0)
        label5 = tk.Label(self, text="No data")
        label5.grid(row=4, column=1)
        while True:
            status, received_val, cipher = self.server.receive_data()
            if status is OK_RECEIVED_MESSAGE:
                label5.config(text=str(received_val))
                self.labeldata2.config(text = cipher)
            else:
                # TODO do a popup connection closed
                # in this case go back to the main server menu
                pass
            # print(received_val)


if __name__ == "__main__":
    app = VPN()
    app.mainloop()
