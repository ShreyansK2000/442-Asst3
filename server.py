#!/usr/bin/env python

import socket
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64

def do_server():

    # RSA keygen
    key = RSA.generate(2048)

    cipher_rsa = PKCS1_OAEP.new(key)
    
    public_key = key.publickey().export_key()

    TCP_IP = '127.0.0.1'
    TCP_PORT = 5005
    BUFFER_SIZE = 4096  # Normally 1024, but we want fast response

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    conn, addr = s.accept()
    print('Connection address:', addr)
    while 1:
        data = conn.recv(BUFFER_SIZE)
        if data.decode("utf-8") == "HELLO":
            print("received connection request")
            print("sending public RSA key")
        
            conn.send(public_key)  # echo
            encrypted_session_key = conn.recv(BUFFER_SIZE)
            session_key = cipher_rsa.decrypt(encrypted_session_key)
            # print("received session key:", session_key)
            # print("received encr session key:",  encrypted_session_key)

        
    conn.close()
