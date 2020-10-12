import socket
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64
import time


def do_client():    
    print("doing client")
    TCP_IP = '127.0.0.1'
    TCP_PORT = 5005
    BUFFER_SIZE = 4096
    INIT_MESSAGE = "I_CLIENT"

    file_in = open("shared-secret.bin", "rb")
    # ciphertext = [ file_in.read(x) for x in (16, 16, -1) ]
    # timestamp = int(time.time())
    # let's assume that the key is somehow available again
    # cipher = AES.new(key, AES.MODE_EAX, nonce)
    # data = cipher.decrypt_and_verify(ciphertext, tag)

    clientKeys = RSA.import_key(open('./keys/client_keys/client-full-pair.pem'))
    serverPublicKey = RSA.import_key(open('./keys/client_keys/client-server-public.pem'))
   
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(INIT_MESSAGE.encode('utf-8'))
    data = s.recv(BUFFER_SIZE)

    # TODO data is something else for authentication
    serverPublicKey = data

    #generate session key
    sessionKey = get_random_bytes(32)
    cipheRSA = PKCS1_OAEP.new(RSA.import_key(serverPublicKey))
    encSessionKey = cipheRSA.encrypt(sessionKey)

    s.send(encSessionKey)

    s.close()
