#!/usr/bin/env python

import socket
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64
from time import time
import struct
import sys
from comm_constants import *


class Server:

    def __init__(self):
        self.comm_socket = None
        self.session_key = None
        self.TCP_PORT = None

    def do_server(self, TCP_PORT=5005, secret_key=None):
        if secret_key is None:
            print("Did not get secret key input, screw you too")
            return ERR_NO_SECRET_KEY, "No Secret Key"

        INIT_MESSAGE = "I_AM_CLIENT"

        self.secret_key = secret_key.encode('utf-8')
        # # get shared secret
        # file_in = open("keys/shared-secret.bin", "rb")
        # secret_key = file_in.read(32)
        # file_in.close()
        # print(secret_key)
        self.TCP_PORT = int(TCP_PORT)

        # connect socket
        self.comm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.comm_socket.bind(('127.0.0.1', self.TCP_PORT))
        self.comm_socket.listen(1)

        try:
            conn, addr = self.comm_socket.accept()
            print('Connection address:', addr)
            while 1:
                data = conn.recv(BUFFER_SIZE)
                if data.decode("utf-8") == INIT_MESSAGE:
                    print("Received connection request")
                    data = conn.recv(BUFFER_SIZE)
                    timestamp = int(time())
                    cipher = AES.new(self.secret_key, AES.MODE_EAX,
                                     struct.pack(">ix", timestamp))
                    plaintext = cipher.decrypt(data)
                    print("authenticated client")
                    # get nonce value
                    (nonce, ) = struct.unpack(">i", plaintext[0:4])
                    # print('nonce', plaintext[0:4])

                    # get session key
                    self.session_key = plaintext[5:]
                    print('server session key', self.session_key)
                    print('session key size', sys.getsizeof(self.session_key))

                    # return nonce + 1
                    auth_return = struct.pack(">ix", int(nonce) + 1)
                    timestamp = int(time())
                    cipher = AES.new(self.secret_key, AES.MODE_EAX,
                                     struct.pack(">ix", timestamp))
                    ciphertext = cipher.encrypt(auth_return)
                    conn.send(ciphertext)
                    # use nonce + 1 for the server side encrypt cipher
                    self.encrypt_cipher = AES.new(
                        self.session_key, AES.MODE_EAX,  struct.pack(">ix", nonce + 1))
                    # use the initial nonce for the server side decrypt cipher
                    self.decrypt_cipher = AES.new(
                        self.session_key, AES.MODE_EAX,  struct.pack(">ix", nonce))
                    self.client_connection = conn
                    self.client_addr = addr
                    # break   # break means authenticated on both side
                    return OK_AUTHENTICATED, "Client Auth OK"

        except socket.error as error:
            print(error)
            return ERR_SOCKET_EXCEPTION, error

    def send_data(self, data_to_send=None):
        if self.comm_socket is None or self.session_key is None:
            print("Authenticated Communication non established")
            return INVALID_SEND_REQ

        if data_to_send is None:
            print("No data to send")
            return INVALID_DATA

        if sys.getsizeof(data_to_send) > BUFFER_SIZE:
            print("Data too large. Please keep less than 4096 bytes")
            return INVALID_DATA

        ciphertext = self.encrypt_cipher.encrypt(data_to_send.encode('utf-8'))
        self.client_connection.send(ciphertext)

    def receive_data(self):

        if self.client_connection is None:
            print("Authenticated Communication non established")
            return INVALID_RECV_REQ

        recv_data = self.client_connection.recv(BUFFER_SIZE)
        print('server received ciphertext: ', recv_data)
        res = self.decrypt_cipher.decrypt(recv_data)
        print('server received plaintext: ', res)
        return res.decode('utf-8')

    # conn.close()
