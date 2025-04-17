import socket
import threading

class ServerConnection:
    def __init__(self, host='localhost', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.lock = threading.Lock()
        print(f"Server started on {host}:{port}")

    def accept_client(self):
        """Accept a new client connection."""
        client_socket, address = self.server_socket.accept()
        return client_socket, address

    def close(self):
        """Close the server socket."""
        self.server_socket.close()