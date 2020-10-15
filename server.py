#!/usr/bin/env python

import socket
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64
import time
import struct

def do_server():
    TCP_IP = '127.0.0.1'
    TCP_PORT = 5005
    BUFFER_SIZE = 4096  # Normally 1024, but we want fast response    
    INIT_MESSAGE = "I_AM_CLIENT"

    # get shared secret
    file_in = open("keys/shared-secret.bin", "rb")
    secret_key = file_in.read(32)
    iv = file_in.read(16)
    iv2 = file_in.read(16)
    file_in.close()
    print(secret_key)
    cipher = AES.new(secret_key, AES.MODE_OFB, iv)

    # connect socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    conn, addr = s.accept()
    print('Connection address:', addr)
    while 1:
        data = conn.recv(BUFFER_SIZE)
        if data.decode("utf-8") == INIT_MESSAGE:
            print("received connection request")
            data = conn.recv(BUFFER_SIZE)
            plaintext = cipher.decrypt(data)
            print("authenticated client") 
            # get nonce value
            (timestamp, ) = struct.unpack(">i", plaintext[0:4])

            # get session key
            session_key = plaintext[5:]

            # return nonce + 1
            cipher = AES.new(secret_key, AES.MODE_OFB, iv2)
            auth_return = struct.pack(">ix", int(timestamp) + 1)
            ciphertext = cipher.encrypt(auth_return)
            conn.send(ciphertext)


        
    conn.close()
