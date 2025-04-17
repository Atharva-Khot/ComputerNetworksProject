class UserInterface:
    def prompt_username(self, message):
        print(message)
        return input("Username: ").strip()

    def display_notification(self, msg):
        print(f"[Notification] {msg}")

    def prompt_question(self, msg):
        print(f"\nQuestion: {msg['question']}")
        for opt in msg['options']:
            print(f"- {opt}")
        return input("Your answer: ").strip()

    def display_result(self, msg):
        print(f"\nCorrect answer: {msg['correct']}")
        print("Scores:")
        for user, score in msg['scores'].items():
            print(f"{user}: {score}")

    def display_game_over(self, msg):
        print("\nGame Over!")
        print("Final Scores:")
        for user, score in msg['scores'].items():
            print(f"{user}: {score}")
        print(f"Winner: {msg['winner']}")

    def display_error(self, msg):
        print(f"Error: {msg}")