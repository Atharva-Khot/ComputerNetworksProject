import threading
from utils.utils import encode_message, decode_stream, MESSAGE_TYPES

class ClientHandler(threading.Thread):
    def __init__(self, conn, addr, clients, scores, broadcast, coordinator):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr
        self.clients = clients
        self.scores = scores
        self.broadcast = broadcast
        self.coordinator = coordinator
        self.buffer = ""
        self.username = None

    def run(self):
        # Handshake: ask for username
        self.conn.send(encode_message({
            "type": MESSAGE_TYPES["welcome"],
            "message": "Enter your username:"
        }))

        # Receive username
        while True:
            data = self.conn.recv(1024).decode()
            if not data:
                return
            self.buffer += data
            for msg, self.buffer in decode_stream(self.buffer):
                if msg.get("type") == MESSAGE_TYPES["username"]:
                    self.username = msg.get("username")
                    break
            if self.username:
                break

        # Check duplicates
        if self.username in self.clients:
            self.conn.send(encode_message({
                "type": MESSAGE_TYPES["error"],
                "message": "Username taken"
            }))
            self.conn.close()
            return

        # Register client
        self.clients[self.username] = self.conn
        self.scores[self.username] = 0
        self.broadcast({
            "type": MESSAGE_TYPES["notification"],
            "message": f"{self.username} joined the quiz!"
        })

        # If first player, start quiz
        if len(self.clients) == 1:
            threading.Thread(target=self.coordinator.run_quiz, daemon=True).start()