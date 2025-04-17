from utils.utils import MESSAGE_TYPES

class MessageHandler:
    def __init__(self, send_func, ui):
        self.send = send_func
        self.ui = ui

    def handle(self, msg):
        t = msg.get("type")
        if t == MESSAGE_TYPES["welcome"]:
            username = self.ui.prompt_username(msg.get("message"))
            self.send({"type": MESSAGE_TYPES["username"], "username": username})

        elif t == MESSAGE_TYPES["lobby"]:
            self.ui.display_lobby(msg.get("message"))

        elif t == MESSAGE_TYPES["notification"]:
            self.ui.display_notification(msg.get("message"))

        elif t == MESSAGE_TYPES["question"]:
            ans = self.ui.prompt_question(msg)
            self.send({"type": MESSAGE_TYPES["answer"], "answer": ans})

        elif t == MESSAGE_TYPES["result"]:
            self.ui.display_result(msg)

        elif t == MESSAGE_TYPES["game_over"]:
            self.ui.display_game_over(msg)

        elif t == MESSAGE_TYPES["error"]:
            self.ui.display_error(msg.get("message"))