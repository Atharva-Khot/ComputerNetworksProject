class UserInterface:
    def prompt_username(self, message): 
        print(message) 
        while True: 
            username = input("Username: ").strip() 
            if username: 
                return username 
            else: 
                print("[Client] Username cannot be blank. Please enter a valid username.")

    def display_lobby(self, msg):
        print(f"[Lobby] {msg}")

    def display_notification(self, msg):
        print(f"[Notification] {msg}")

    def prompt_question(self, msg):
        print(f"\nQuestion {msg['number']}: {msg['question']}")
        for opt in msg['options']:
            print(f"- {opt}")
        return input("Your answer: ")

    def display_result(self, msg):
        print(f"\nResult Q{msg['number']}: Correct answer: {msg['correct']}")
        print("Scores:")
        for u, s in msg['scores'].items():
            print(f"{u}: {s}")

    def display_game_over(self, msg):
        print("\nGame Over!")
        print("Final Scores:")
        for u, s in msg['scores'].items():
            print(f"{u}: {s}")
        print(f"Winner: {msg['winner']}")

    def display_error(self, msg):
        print(f"Error: {msg}")