import socket
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256, HMAC
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

    def execute(self, debug=False, step=None):
        if not debug:
            ret1 = self.initComms()
            ret2 = self.encryptClientAuth()
            ret3 = self.waitAuthResponse()
            return ret3

        elif step == 1:
            return self.initComms()

        elif step == 2:
            return self.encryptClientAuth()

        elif step == 3:
            return self.waitAuthResponse()

    def establish_connection(self, TCP_IP='127.0.0.1', TCP_PORT=5005, secret_key=None):
        print("doing client")

        if secret_key is None:
            print("Did not get secret key input, screw you too")
            return ERR_NO_SECRET_KEY, "No Secret Key"

        self.TCP_IP = TCP_IP
        self.TCP_PORT = int(TCP_PORT)
        # establish HMAC using secret value
        self.mac = HMAC.new(secret_key.encode('utf-8'), digestmod=SHA256)

        self.INIT_MESSAGE = "I_AM_CLIENT"
        hash_object = SHA256.new()
        hash_object.update(secret_key.encode('utf-8'))
        self.secret_key = hash_object.digest()

    def initComms(self):
        # send id message

        try:
            self.comm_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.comm_socket.connect((self.TCP_IP, self.TCP_PORT))
            self.comm_socket.send(self.INIT_MESSAGE.encode('utf-8'))

            return STEP_RETURN_1, self.INIT_MESSAGE

        except socket.error as error:
            print(error)
            return ERR_SOCKET_EXCEPTION, error

    def encryptClientAuth(self):

        try:
            timestamp = int(time())
            # generate session key
            self.session_key = get_random_bytes(32)
            print('client session key', self.session_key)

            h = SHA256.new()
            h.update(self.secret_key + self.session_key)
            hash_out = h.digest()
            print('client hash', hash_out)

            # encrypt bytestream
            print("timestamp: " + str(timestamp))
            auth_msg = struct.pack(">ix", timestamp) + \
                self.session_key + hash_out
            print(self.session_key)
            # print("num bytes: " + str(struct.pack(">i", timestamp).size))
            cipher = AES.new(self.secret_key, AES.MODE_EAX,
                             struct.pack(">ix", timestamp))
            ciphertext = cipher.encrypt(auth_msg)

            self.comm_socket.send(ciphertext)

            return STEP_RETURN_2, ciphertext
        except socket.error as error:
            print(error)
            return ERR_SOCKET_EXCEPTION, error

    def waitAuthResponse(self):
        # get nonce back
        try:
            data = self.comm_socket.recv(BUFFER_SIZE)
            timestamp = int(time())
            cipher = AES.new(self.secret_key, AES.MODE_EAX,
                             struct.pack(">ix", timestamp))
            plaintext = cipher.decrypt(data)
            (ret_timestamp, ) = struct.unpack(">i", plaintext[0:4])
            # time skew? offer 3 seconds???
            # this clock skew check is not correct
            if timestamp <= ret_timestamp <= timestamp + 3:
                print("authenticated server")
                # use returned nonce + 1 for the client side decrypt cipher
                self.decrypt_cipher = AES.new(
                    self.session_key, AES.MODE_EAX,  struct.pack(">ix", ret_timestamp))
                # use original nonce for the client side encrypt cipher
                self.encrypt_cipher = AES.new(
                    self.session_key, AES.MODE_EAX,  struct.pack(">ix", timestamp))
                return OK_AUTHENTICATED, "Server Auth OK"
            # TODO: FIX AUTHENTICATION OF SERVER HERE!!!

            print(ret_timestamp)
        except socket.error as error:
            print(error)
            return ERR_SOCKET_EXCEPTION, error

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

        client_to_send = data_to_send.encode('utf-8')
        print('client send plaintext: ', client_to_send)
        self.mac.update(client_to_send)
        ciphertext = self.encrypt_cipher.encrypt(
            self.mac.digest() + data_to_send.encode('utf-8'))
        # TODO: implement received data:

        try:
            self.comm_socket.send(ciphertext)
            print('client send ciphertext: ', ciphertext)

            return OK_SENT_MESSAGE, ciphertext
        except socket.error as error:
            print(error)
            return ERR_SOCKET_EXCEPTION, error

    def receive_data(self):

        if self.comm_socket is None:
            print("Authenticated Communication non established")
            return INVALID_RECV_REQ, "Authenticated Communication non established", "None"

        try:
            recv_data = self.comm_socket.recv(BUFFER_SIZE)
            plaintext = self.decrypt_cipher.decrypt(recv_data)
            recv_mac = plaintext[0:32]
            msg = plaintext[32:]
            self.mac.update(msg)
            self.mac.verify(recv_mac)
            return OK_RECEIVED_MESSAGE, msg.decode('utf-8'), recv_data
        except ValueError:
            return ERR_HMAC_EXCEPTION, "HMAC signature does not match", "None"
        except socket.error as error:
            return ERR_SOCKET_EXCEPTION, error, "None"
