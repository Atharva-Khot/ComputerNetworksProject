import threading
from utils.utils import encode_message, decode_stream, MESSAGE_TYPES

class ClientHandler(threading.Thread):
    def __init__(self, conn, addr, lobby, active, blocked):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr
        self.lobby = lobby
        self.active = active
        self.blocked = blocked
        self.buffer = ""
        self.username = None

    def run(self):
        # Ask for username
        self.conn.send(encode_message({
            "type": MESSAGE_TYPES["welcome"],
            "message": "Enter your username:"
        }))

        # Receive it
        while True:
            data = self.conn.recv(1024).decode()
            if not data:
                return
            self.buffer += data
            for msg, self.buffer in decode_stream(self.buffer):
                if msg.get("type") == MESSAGE_TYPES["username"]:
                    self.username = msg["username"].strip()
                    break
            if self.username:
                break

        # Blocked?
        if self.username in self.blocked:
            self.conn.send(encode_message({
                "type": MESSAGE_TYPES["error"],
                "message": "You are blocked from this server."
            }))
            self.conn.close()
            return

        # Duplicate?
        if self.username in self.lobby or self.username in self.active:
            self.conn.send(encode_message({
                "type": MESSAGE_TYPES["error"],
                "message": "Username already in use."
            }))
            self.conn.close()
            return

        # Join lobby
        self.lobby[self.username] = self.conn
        print(f"[Server] {self.username} joined lobby from {self.addr}")
        self.conn.send(encode_message({
            "type": MESSAGE_TYPES["lobby"],
            "message": "Waiting for admin to start the quiz..."
        }))

        # Notify everyone (lobby + active)
        for sock in list(self.lobby.values()) + list(self.active.values()):
            try:
                sock.send(encode_message({
                    "type": MESSAGE_TYPES["notification"],
                    "message": f"{self.username} has entered the lobby."
                }))
            except:
                pass

        # And return—further interaction happens once admin moves them to `active`
