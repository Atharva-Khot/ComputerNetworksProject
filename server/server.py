from networking.server_connection import ServerConnection
from core.scoreboard import Scoreboard
from core.quiz_coordinator import QuizCoordinator
from server.client_handler import ClientHandler

# Shared state
def main():
    server_conn = ServerConnection()
    clients = {}      # username -> socket
    scoreboard = Scoreboard()
    questions = __import__('utils.utils', fromlist=['load_questions']).load_questions()

    def broadcast(msg):
        from utils.utils import encode_message
        data = encode_message(msg)
        with server_conn.lock:
            for sock in clients.values():
                try:
                    sock.send(data)
                except:
                    pass

    coordinator = QuizCoordinator(clients, scoreboard.get_scores(), questions, broadcast)

    print(f"Server listening on {server_conn.socket.getsockname()}")
    while True:
        conn, addr = server_conn.accept_client()
        handler = ClientHandler(conn, addr, clients, scoreboard.get_scores(), broadcast, coordinator)
        handler.start()

if __name__ == "__main__":
    main()