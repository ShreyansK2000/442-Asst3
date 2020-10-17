#!/usr/bin/env python

import socket
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
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

    def execute(self, debug=False, step=None):
        if not debug:
            ret1 = self.awaitConnectionRequest()
            ret2 = self.awaitAndEvaluateEncryptedMessage()
            ret3 = self.respondAuthenticated()
            return ret3

        elif step == 1:
            return self.awaitConnectionRequest()

        elif step == 2:
            return self.awaitAndEvaluateEncryptedMessage()
        
        elif step == 3:
            return self.respondAuthenticated()

    def listen_connections(self, TCP_PORT=5005, secret_key=None):
        if secret_key is None:
            print("Did not get secret key input, screw you too")
            return ERR_NO_SECRET_KEY, "No Secret Key"

        self.CLNT_INIT_MESSAGE = "I_AM_CLIENT"

        hash_object = SHA256.new()
        hash_object.update(secret_key.encode('utf-8'))
        self.secret_key = hash_object.digest()
        print('server hashed secret key', self.secret_key)
        # # get shared secret
        # file_in = open("keys/shared-secret.bin", "rb")
        # secret_key = file_in.read(32)
        # file_in.close()
        # print(secret_key)
        self.TCP_PORT = int(TCP_PORT)

        # connect socket
        self.comm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.comm_socket.bind(('0.0.0.0', self.TCP_PORT))
        self.comm_socket.listen(1)
        

        # try:
        #     self.conn, addr = self.comm_socket.accept()
        #     print('Connection address:', addr)
            
        #     data = conn.recv(BUFFER_SIZE)
        #     if data.decode("utf-8") == INIT_MESSAGE:
        #         print("Received connection request")
        #         data = conn.recv(BUFFER_SIZE)
        #         timestamp = int(time())
        #         cipher = AES.new(self.secret_key, AES.MODE_EAX,
        #                             struct.pack(">ix", timestamp))
        #         plaintext = cipher.decrypt(data)
        #         # print("authenticated client")
        #         # get nonce value
        #         (nonce, ) = struct.unpack(">i", plaintext[0:4])
        #         # print('nonce', plaintext[0:4])

        #         # get session key
        #         # print("client rcvd secret key", client_secret_key)
        #         session_key_from_client = plaintext[5:37]
        #         hash_from_client = plaintext[37:]
        #         print("client session key", session_key_from_client)
        #         print('server reading client hash', hash_from_client)


        #         compute_hash = SHA256.new()
        #         compute_hash.update(self.secret_key + session_key_from_client)

                # if hash_from_client == compute_hash.digest():
                #     print("authenticated client")
                #     self.session_key = session_key_from_client
                #     print('server session key', self.session_key)
                #     print('session key size', sys.getsizeof(self.session_key))

                #     # return nonce + 1
                #     auth_return = struct.pack(">ix", int(time()) + 1)
                #     timestamp = int(time())
                #     cipher = AES.new(self.secret_key, AES.MODE_EAX,
                #                     struct.pack(">ix", timestamp))
                #     ciphertext = cipher.encrypt(auth_return)
                #     conn.send(ciphertext)
                #     # use nonce + 1 for the server side encrypt cipher
                #     self.encrypt_cipher = AES.new(
                #         self.session_key, AES.MODE_EAX,  struct.pack(">ix", timestamp + 1))
                #     # use the initial nonce for the server side decrypt cipher
                #     self.decrypt_cipher = AES.new(
                #         self.session_key, AES.MODE_EAX,  struct.pack(">ix", nonce))
                #     self.client_connection = self.conn
                #     self.client_addr = addr
                    # break   # break means authenticated on both side
                    # return OK_AUTHENTICATED, "Client Auth OK"
        #         else: 
        #             print("invalid client")
        #             return ERR_UNAUTHENTICATED_REQ , "Invalid client"


                    
        # except socket.error as error:
        #     print(error)
        #     return ERR_SOCKET_EXCEPTION, error

    def awaitConnectionRequest(self):
        try:
            self.conn, addr = self.comm_socket.accept()
            print('Connection address:', addr)
            
            connReqData = self.conn.recv(BUFFER_SIZE)
            self.receivedConnectionReq = connReqData.decode("utf-8") == self.CLNT_INIT_MESSAGE            
            if not self.receivedConnectionReq:
                return ERR_INVALID_CONN_REQ, "Invalid initiation message"
            else:
                return SERVER_RECEIVED_CONN_REQ, connReqData.decode("utf-8")
        except socket.error as error:
            print(error)
            return ERR_SOCKET_EXCEPTION, error

    def awaitAndEvaluateEncryptedMessage(self):
        print("Received connection request")
        try:
            if self.receivedConnectionReq:
                data = self.conn.recv(BUFFER_SIZE)

                timestamp = int(time())
                cipher = AES.new(self.secret_key, AES.MODE_EAX,
                                    struct.pack(">ix", timestamp))
                plaintext = cipher.decrypt(data)
                # get nonce value
                (self.nonce, ) = struct.unpack(">i", plaintext[0:4])
                # print('nonce', plaintext[0:4])

                # get session key
                # print("client rcvd secret key", client_secret_key)
                session_key_from_client = plaintext[5:37]
                hash_from_client = plaintext[37:]
                print("client session key", session_key_from_client)
                print('server reading client hash', hash_from_client)


                compute_hash = SHA256.new()
                compute_hash.update(self.secret_key + session_key_from_client)

                if hash_from_client == compute_hash.digest():
                    self.client_authenticated = True
                    self.session_key = session_key_from_client
                    return SERVER_RECEIVED_AUTH_MESSAGE, data
                else:
                    return ERR_UNAUTHENTICATED_REQ, "Invalid Client"
                    
            else:
                ERR_UNAUTHENTICATED_REQ,  "Can't step after invalid connection request"
        except socket.error as error:
            print(error)
            return ERR_SOCKET_EXCEPTION, error

    def respondAuthenticated(self):
        try:
            if self.client_authenticated:
                print("authenticated client")

                # return nonce + 1
                auth_return = struct.pack(">ix", int(time()) + 1)
                timestamp = int(time())
                cipher = AES.new(self.secret_key, AES.MODE_EAX,
                                struct.pack(">ix", timestamp))
                ciphertext = cipher.encrypt(auth_return)
                self.conn.send(ciphertext)

                self.encrypt_cipher = AES.new(self.session_key, AES.MODE_EAX,  struct.pack(">ix", self.nonce + 1))
                # use the initial nonce for the server side decrypt cipher
                self.decrypt_cipher = AES.new(self.session_key, AES.MODE_EAX,  struct.pack(">ix", self.nonce))
                self.client_connection = self.conn
                return OK_AUTHENTICATED, ciphertext
            else:
                return ERR_UNAUTHENTICATED_REQ, "Invalid Client!"
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
            return INVALID_RECV_REQ, "Authenticated Communication non established"

        try:
            recv_data = self.client_connection.recv(BUFFER_SIZE)
            return OK_RECEIVED_MESSAGE, self.decrypt_cipher.decrypt(recv_data).decode('utf-8')
        except socket.error as error:
            return ERR_SOCKET_EXCEPTION, error

    # conn.close()
