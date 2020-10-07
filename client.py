import socket
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64


def do_client():    
    TCP_IP = '127.0.0.1'
    TCP_PORT = 5005
    BUFFER_SIZE = 4096
    INIT_MESSAGE = "HELLO"
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(INIT_MESSAGE.encode('utf-8'))
    data = s.recv(BUFFER_SIZE)

    serverPublicKey = data
    # print(serverPublicKey)

    #generate session key
    session_key = get_random_bytes(16)
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(serverPublicKey))
    enc_session_key = cipher_rsa.encrypt(session_key)

    s.send(enc_session_key)

    # print("session key: ", session_key)
    # print("encrypted key: ", enc_session_key)



    s.close()

    # print("received data:", data.decode('utf-8'))
