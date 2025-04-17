import threading
import time
from client_connection import ClientConnection
from message_handler import MessageHandler
from user_interface import UserInterface

class QuizClient:
    def __init__(self):
        self.connection = ClientConnection()
        self.message_handler = MessageHandler(self.connection.send)
        self.ui = UserInterface(self.connection.send)
        self.running = True

    def receive_messages(self):
        """Receive and process server messages."""
        while self.running:
            try:
                message = self.connection.receive()
                result = self.message_handler.handle_message(message)
                if result is False:
                    self.running = False
                elif isinstance(result, dict) and result["type"] == "question":
                    self.ui.start_answer_thread(result["timeout"], message["number"])
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.running = False
                break

    def start(self):
        """Start the client."""
        try:
            # Start receiving messages
            threading.Thread(target=self.receive_messages, daemon=True).start()

            # Keep client running
            while self.running:
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nDisconnecting...")
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            self.running = False
            self.connection.close()

if __name__ == "__main__":
    client = QuizClient()
    client.start()