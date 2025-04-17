import threading
from utils import encode_message, decode_message, MESSAGE_TYPES

class ClientHandler:
    def __init__(self, client_socket, address, clients, scores, broadcast_callback, answer_callback):
        self.client_socket = client_socket
        self.address = address
        self.clients = clients
        self.scores = scores
        self.broadcast_callback = broadcast_callback
        self.answer_callback = answer_callback
        self.username = None
        self.lock = threading.Lock()

    def handle(self):
        """Handle client connection and messages."""
        try:
            # Request username
            self.client_socket.send(encode_message({
                "type": MESSAGE_TYPES["welcome"],
                "message": "Enter your username:"
            }))
            data = decode_message(self.client_socket.recv(1024))
            self.username = data.get("username", f"Guest_{self.address[1]}")

            with self.lock:
                if self.username in self.clients:
                    self.client_socket.send(encode_message({
                        "type": MESSAGE_TYPES["error"],
                        "message": "Username taken"
                    }))
                    self.client_socket.close()
                    return
                self.clients[self.username] = (self.client_socket, self.address)
                self.scores[self.username] = 0

            self.broadcast_callback({
                "type": MESSAGE_TYPES["notification"],
                "message": f"{self.username} joined the game!"
            })

            # Handle client messages
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                message = decode_message(data)
                if message["type"] in [MESSAGE_TYPES["answer"], MESSAGE_TYPES["hint"]]:
                    self.answer_callback(self.username, message)
                else:
                    self.answer_callback(self.username, message)

        except Exception as e:
            print(f"Error handling client {self.address}: {e}")
        finally:
            self.remove_client()

    def remove_client(self):
        """Remove client from registry."""
        with self.lock:
            if self.username in self.clients:
                del self.clients[self.username]
                self.client_socket.close()
                self.broadcast_callback({
                    "type": MESSAGE_TYPES["notification"],
                    "message": f"{self.username} left the game!"
                })