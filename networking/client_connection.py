import socket
from config import HOST, PORT
from utils.utils import encode_message

class ClientConnection:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect((HOST, PORT))

    def send(self, msg):
        # msg is a dict
        self.socket.send(encode_message(msg))

    def receive(self, bufsize=1024):
        return self.socket.recv(bufsize)

    def close(self):
        self.socket.close()