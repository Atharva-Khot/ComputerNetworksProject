import threading
from networking.server_connection import ServerConnection
from core.scoreboard import Scoreboard
from core.quiz_coordinator import QuizCoordinator
from server.client_handler import ClientHandler
from utils.utils import load_questions, MESSAGE_TYPES, encode_message

# Shared state
def main():
    server_conn = ServerConnection()
    lobby = {}        # username -> socket
    active = {}
    scoreboard = Scoreboard()
    questions = load_questions()
    coordinator = None

    def broadcast_to_active(msg):
        data = encode_message(msg)
        with server_conn.lock:
            for sock in active.values():
                try:
                    sock.send(data)
                except:
                    pass

    # Admin console for starting quizzes
    def admin_console():
        nonlocal coordinator, active, lobby, scoreboard
        while True:
            cmd = input("[Server] Type 'start' to begin quiz: ")
            if cmd.strip().lower() == 'start' and lobby:
                # Move all lobby to active
                active = lobby.copy()
                lobby.clear()
                scoreboard.reset()
                coordinator = QuizCoordinator(active, scoreboard.get_scores(), questions, broadcast_to_active)
                coordinator.start()
            else:
                print("[Server] No players in lobby or invalid command")

    threading.Thread(target=admin_console, daemon=True).start()

    print(f"[Server] Listening on {server_conn.socket.getsockname()}")
    while True:
        conn, addr = server_conn.accept_client()
        handler = ClientHandler(conn, addr, lobby, active, broadcast_to_active)
        handler.start()

if __name__ == "__main__":
    main()