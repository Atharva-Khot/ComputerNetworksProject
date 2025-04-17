import threading
from server_connection import ServerConnection
from client_handler import ClientHandler
from quiz_coordinator import QuizCoordinator
from scoreboard import Scoreboard
from utils import encode_message

class QuizServer:
    def __init__(self):
        self.clients = {}
        self.scoreboard = Scoreboard()
        self.server_connection = ServerConnection()
        self.quiz_coordinator = QuizCoordinator(
            self.clients,
            self.scoreboard.get_scores(),
            self.broadcast
        )

    def broadcast(self, message):
        """Broadcast message to all clients."""
        message = encode_message(message)
        with self.server_connection.lock:
            for client_socket in [c[0] for c in self.clients.values()]:
                try:
                    client_socket.send(message)
                except:
                    continue

    def start(self):
        """Start the server."""
        # Start quiz in a separate thread
        threading.Thread(target=self.quiz_coordinator.run_quiz, daemon=True).start()

        while True:
            try:
                client_socket, address = self.server_connection.accept_client()
                # Handle client in a separate thread
                handler = ClientHandler(
                    client_socket,
                    address,
                    self.clients,
                    self.scoreboard.get_scores(),
                    self.broadcast,
                    self.quiz_coordinator.process_answer
                )
                threading.Thread(
                    target=handler.handle,
                    daemon=True
                ).start()
            except KeyboardInterrupt:
                print("\nShutting down server...")
                break
            except Exception as e:
                print(f"Server error: {e}")

        self.server_connection.close()

if __name__ == "__main__":
    server = QuizServer()
    server.start()