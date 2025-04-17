import socket
import threading
from config import HOST, PORT

class ServerConnection:
    def __init__(self):
        self.lock = threading.Lock()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen()

    def accept_client(self):
        return self.socket.accept()

    def close(self):
        self.socket.close()