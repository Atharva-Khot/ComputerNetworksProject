import threading
from utils.utils import encode_message, decode_stream, MESSAGE_TYPES

class ClientHandler(threading.Thread):
    def __init__(self, conn, addr, lobby, active, broadcast):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr
        self.lobby = lobby          # dict: username -> socket
        self.active = active        # dict: username -> socket
        self.broadcast = broadcast
        self.buffer = ""
        self.username = None

    def run(self):
        # Send welcome and lobby status
        self.conn.send(encode_message({"type": MESSAGE_TYPES["welcome"], "message": "Enter your username:"}))

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

        # Duplicate username check
        if self.username in self.lobby or self.username in self.active:
            self.conn.send(encode_message({"type": MESSAGE_TYPES["error"], "message": "Username taken"}))
            self.conn.close()
            return

        # Register in lobby
        self.lobby[self.username] = self.conn
        print(f"[Server] {self.username} joined lobby from {self.addr}")
        self.conn.send(encode_message({"type": MESSAGE_TYPES["lobby"], "message": "Waiting for quiz to start..."}))
        self.broadcast({"type": MESSAGE_TYPES["notification"], "message": f"{self.username} is in the lobby"})