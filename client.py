import socket
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64
from time import time
import struct
from comm_constants import *
import sys

class Client():
    
    def __init__(self):
        self.comm_socket = None
        self.session_key = None
        self.TCP_IP = None
        self.TCP_PORT = None

    def establish_connection(self, TCP_IP='127.0.0.1', TCP_PORT=5005, secret_key=None):
        print("doing client")

        if secret_key is None:
            print("Did not get secret key input, screw you too")
            return (ERR_NO_SECRET_KEY, "No Secret Key")

        self.TCP_IP = TCP_IP
        self.TCP_PORT = int(TCP_PORT)
        self.secret_key = secret_key
        
        INIT_MESSAGE = "I_AM_CLIENT"

        # get shared secret
        # TODO this is inputted by the TA in GUI
        # file_in = open("keys/shared-secret.bin", "rb")
        # secret_key = file_in.read(32)
        # file_in.close()

        
        print(secret_key)

        # connect socket
        self.comm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.comm_socket.connect((self.TCP_IP, self.TCP_PORT))

            # create initial message
            # nonce timestamp
            timestamp = int(time())
            # generate session key
            self.session_key = get_random_bytes(32)
            # encrypt bytestream
            print("timestamp: " + str(timestamp))
            auth_msg = struct.pack(">ix", timestamp) + self.session_key
            print(self.session_key)
            # print("num bytes: " + str(struct.pack(">i", timestamp).size))
            cipher = AES.new(secret_key, AES.MODE_EAX, struct.pack(">ix", timestamp))
            ciphertext = cipher.encrypt(auth_msg)

            # send id message
            self.comm_socket.send(INIT_MESSAGE.encode('utf-8'))
            # send encrypted nonce and key
            self.comm_socket.send(ciphertext)

            # get nonce back
            data = self.comm_socket.recv(BUFFER_SIZE)
            timestamp = int(time())
            cipher = AES.new(secret_key, AES.MODE_EAX, struct.pack(">ix", timestamp))
            plaintext = cipher.decrypt(data)
            (ret_timestamp, ) = struct.unpack(">i", plaintext[0:4])
            # time skew? offer 3 seconds???
            if ret_timestamp == timestamp + 3:
                print("authenticated server")
                self.cipher = AES.new(self.session_key, AES.MODE_EAX,  struct.pack(">ix", ret_timestamp))
                return (OK_AUTHENTICATED, "Server Auth OK")
            # TODO: what happens if not authenticated?

            print(ret_timestamp)
        except socket.error as error:
            print(error)
            return (ERR_SOCKET_EXCEPTION, error)

            # TODO move this to after comm is finished
            # self.comm_socket.close()
        

    def send_data(self, data_to_send=None):
        if self.comm_socket is None or self.session_key is None or self.TCP_IP is None:
            print("Authenticated Communication non established")
            return INVALID_SEND_REQ

        if data_to_send is None:
            print("No data to send")
            return INVALID_DATA

        if sys.getsizeof(data_to_send) > BUFFER_SIZE:
            print("Data too large. Please keep less than 4096 bytes")
            return INVALID_DATA

        ciphertext = self.cipher.encrypt(data_to_send.encode('utf-8'))
        self.comm_socket.send(ciphertext)
        # TODO: implement received data: 

    def receive_data(self):

        if self.comm_socket is None: 
            print("Authenticated Communication non established")
            return INVALID_RECV_REQ

    
        recv_data = self.comm_socket.recv(BUFFER_SIZE)
        self.cipher.decrypt(recv_data)
        return recv_data.decode('utf-8')


        

