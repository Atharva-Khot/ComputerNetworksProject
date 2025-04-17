import socket
from utils import encode_message, decode_message

class ClientConnection:
    def __init__(self, host='localhost', port=12345):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

    def send(self, message):
        """Send a message to the server."""
        self.client_socket.send(encode_message(message))

    def receive(self):
        """Receive a message from the server."""
        data = self.client_socket.recv(1024)
        if not data:
            return None
        return decode_message(data)

    def close(self):
        """Close the client socket."""
        self.client_socket.close()