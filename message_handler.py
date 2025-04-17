from utils import MESSAGE_TYPES

class MessageHandler:
    def __init__(self, send_callback):
        self.send_callback = send_callback
        self.username = None
        self.current_question = None

    def handle_message(self, message):
        """Handle a received server message."""
        if not message:
            return False

        if message["type"] == MESSAGE_TYPES["welcome"]:
            print(message["message"])
            self.username = input("Username: ")
            self.send_callback({
                "type": MESSAGE_TYPES["username"],
                "username": self.username
            })

        elif message["type"] == MESSAGE_TYPES["category"]:
            print("\nAvailable categories:", ", ".join(message["categories"]))
            category = input("Choose a category: ").strip()
            self.send_callback(category)

        elif message["type"] == MESSAGE_TYPES["ready"]:
            print(f"\n{message['message']}")
            response = input("Enter y/n: ").strip()
            self.send_callback(response)

        elif message["type"] == MESSAGE_TYPES["question"]:
            print(f"\nQuestion {message['number']}: {message['question']} ({message['difficulty']}, {message['points']} points)")
            for option in message['options']:
                print(option)
            print(f"Time remaining: {message['timeout']} seconds")
            print("Type 'hint' to request a hint (-2 points)")
            self.current_question = message["number"]
            return {"type": "question", "timeout": message["timeout"]}

        elif message["type"] == MESSAGE_TYPES["hint"]:
            print(f"\n[Hint] {message['message']}")
            print(f"Current score: {message['score']}")

        elif message["type"] == MESSAGE_TYPES["results"]:
            print("\nResults:")
            print(f"Correct answer: {message['correct_answer']}")
            if self.username in message["individual_results"]:
                status = "Correct!" if message["individual_results"][self.username] else "Wrong!"
                print(f"Your answer: {status}")
            print("\nCurrent Scores:")
            for player, score in message["scores"].items():
                print(f"{player}: {score}")

        elif message["type"] == MESSAGE_TYPES["game_over"]:
            print("\nGame Over!")
            print("Final Scores:")
            for player, score in message["scores"].items():
                print(f"{player}: {score}")
            if message["winner"]:
                print(f"Winner: {message['winner']}")
            return True  # Continue for rematch prompt

        elif message["type"] == MESSAGE_TYPES["rematch"]:
            print(f"\n{message['message']}")
            response = input("Enter y/n: ").strip()
            self.send_callback(response)

        elif message["type"] == MESSAGE_TYPES["notification"]:
            print(f"\n[Notification] {message['message']}")

        elif message["type"] == MESSAGE_TYPES["error"]:
            print(f"Error: {message['message']}")
            return False

        return True