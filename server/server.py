import threading, sys
from networking.server_connection import ServerConnection
from core.scoreboard import Scoreboard
from core.quiz_coordinator import QuizCoordinator
from server.client_handler import ClientHandler
from utils.utils import load_questions, MESSAGE_TYPES, encode_message
from config import HOST, PORT, QUESTION_TIMEOUT

def main():
    server_conn = ServerConnection()
    lobby = {}        # waiting
    active = {}       # in-game
    blocked = set()   # usernames we won’t allow
    scoreboard = Scoreboard()
    questions = load_questions()
    coordinator = None

    def broadcast_active(msg):
        data = encode_message(msg)
        with server_conn.lock:
            for sock in active.values():
                try: sock.send(data)
                except: pass
                
                
    def move_active_to_lobby():
        nonlocal lobby, active
        print("[Server] Moving all active players back to lobby")
        for user, sock in list(active.items()):
            # notify
            try:
                sock.send(encode_message({
                    "type": MESSAGE_TYPES["notification"],
                    "message": "Quiz has ended — returning you to the lobby."
                }))
                sock.send(encode_message({
                    "type": MESSAGE_TYPES["lobby"],
                    "message": "Waiting for next quiz…"
                }))
            except:
                pass
            # move
            lobby[user] = sock
        active.clear()

    def admin_console():
        nonlocal coordinator, lobby, active, scoreboard
        while True:
            cmd = input("[Server Admin] > ").strip()
            if cmd == "i":
                print(f" Lobby: {list(lobby.keys())}")
                print(f" Active: {list(active.keys())}")

            elif cmd.startswith("kick "):
                user = cmd.split(None,1)[1]
                for d in (lobby, active):
                    if user in d:
                        sock = d.pop(user)
                        sock.send(encode_message({"type": MESSAGE_TYPES["notification"],
                                                  "message": "You have been kicked."}))
                        sock.close()
                        print(f"[Server] Kicked {user}")
                        break

            elif cmd.startswith("block "):
                user = cmd.split(None,1)[1]
                blocked.add(user)
                # also kick if present
                for d in (lobby, active):
                    if user in d:
                        sock = d.pop(user)
                        sock.send(encode_message({"type": MESSAGE_TYPES["notification"],
                                                  "message": "You have been blocked."}))
                        sock.close()
                print(f"[Server] Blocked {user}")

            elif cmd == "end game":
                if coordinator:
                    coordinator.stop()
                    print("[Admin] Moving players back to lobby...")
                    for user, sock in list(active.items()):
                        # notify game over / lobby
                        sock.send(encode_message({
                            "type": MESSAGE_TYPES["notification"],
                            "message": "Quiz has been ended by the server."
                        }))
                        sock.send(encode_message({
                            "type": MESSAGE_TYPES["lobby"],
                            "message": "You are now back in the lobby. Waiting for next quiz..."
                        }))
                        lobby[user] = sock
                    active.clear()
                else:
                    print("[Admin] No quiz running")

            elif cmd == "start":
                if lobby:
                    # move everyone from lobby → active
                    active = lobby.copy(); lobby.clear()
                    scoreboard.reset()
                    coordinator = QuizCoordinator(active, scoreboard.get_scores(),
                                                  questions, broadcast_active, timeout=QUESTION_TIMEOUT, on_quiz_end=move_active_to_lobby)
                    coordinator.start()
                else:
                    print("[Admin] No players in lobby")

            elif cmd == "exit":
                print("[Admin] Shutting down.")
                # close all sockets
                for s in list(lobby.values()) + list(active.values()):
                    try: s.close()
                    except: pass
                server_conn.close()
                sys.exit(0)

            else:
                print("[Admin] Unknown command. Options: i, start, end game, kick <user>, block <user>, exit")

    # start admin console thread
    threading.Thread(target=admin_console, daemon=True).start()

    print(f"[Server] Listening on {server_conn.socket.getsockname()}")
    while True:
        conn, addr = server_conn.accept_client()
        # immediately hand off to ClientHandler, which will place them in `lobby`
        handler = ClientHandler(conn, addr, lobby, active, blocked)
        handler.start()

if __name__ == "__main__":
    main()
