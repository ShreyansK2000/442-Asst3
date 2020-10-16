import socket
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64
from time import time
import struct

# Tung - I suggest this function takes parameter from the GUI
# def do_client(TCP_IP, TCP_PORT, data)


def do_client():
    print("doing client")
    TCP_IP = '127.0.0.1'
    TCP_PORT = 5005
    BUFFER_SIZE = 4096
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
    s.connect((TCP_IP, TCP_PORT))

    # create initial message
    # nonce timestamp
    timestamp = int(time())
    # generate session key
    session_key = get_random_bytes(32)
    # encrypt bytestream
    print("timestamp: " + str(timestamp))
    auth_msg = struct.pack(">ix", timestamp) + session_key
    print(session_key)
    # print("num bytes: " + str(struct.pack(">i", timestamp).size))
    ciphertext = cipher.encrypt(auth_msg)

    # send id message
    s.send(INIT_MESSAGE.encode('utf-8'))
    # send encrypted nonce and key
    s.send(ciphertext)

    # get nonce back
    data = s.recv(BUFFER_SIZE)
    cipher = AES.new(secret_key, AES.MODE_OFB, iv2)
    plaintext = cipher.decrypt(data)
    (ret_timestamp, ) = struct.unpack(">i", plaintext[0:4])
    # time skew? offer 3 seconds???
    if ret_timestamp < timestamp + 3:
        print("authenticated server")
    # TODO: what happens if not authenticated?

    s.close()
