import threading
from networking.client_connection import ClientConnection
from client.message_handler import MessageHandler
from client.user_interface import UserInterface
from utils.utils import decode_stream, MESSAGE_TYPES


def main():
    conn = ClientConnection()
    conn.connect()
    ui = UserInterface()
    handler = MessageHandler(conn.send, ui)
    buffer = ""

    try:
        while True:
            data = conn.receive().decode()
            if not data:
                break
            buffer += data
            for msg, buffer in decode_stream(buffer):
                handler.handle(msg)
                if msg.get("type") == MESSAGE_TYPES["game_over"]:
                    return
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()