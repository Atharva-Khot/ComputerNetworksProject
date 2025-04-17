import time
import queue
import random
from utils import QUESTIONS, MESSAGE_TYPES, encode_message

class QuizCoordinator:
    def __init__(self, clients, scores, broadcast_callback):
        self.clients = clients
        self.scores = scores
        self.broadcast_callback = broadcast_callback
        self.question_timeout = 10  # seconds
        self.current_answers = None
        self.current_hints = {}  # Track hint usage per player
        self.selected_category = None

    def select_category(self):
        """Broadcast category selection prompt and select most voted category."""
        categories = list(QUESTIONS.keys())
        self.broadcast_callback({
            "type": MESSAGE_TYPES["category"],
            "categories": categories
        })
        time.sleep(5)  # Allow time for category votes
        votes = {}
        while not self.current_answers.empty():
            username, category = self.current_answers.get()
            if category in categories:
                votes[category] = votes.get(category, 0) + 1
        # Select category with most votes or random
        self.selected_category = max(votes.items(), key=lambda x: x[1])[0] if votes else random.choice(categories)
        self.broadcast_callback({
            "type": MESSAGE_TYPES["notification"],
            "message": f"Selected category: {self.selected_category}"
        })

    def check_readiness(self):
        """Check if all clients are ready to start."""
        ready_clients = set()
        self.current_answers = queue.Queue()
        self.broadcast_callback({
            "type": MESSAGE_TYPES["ready"],
            "message": "Are you ready? (y/n)"
        })
        time.sleep(5)  # Wait for readiness responses
        while not self.current_answers.empty():
            username, response = self.current_answers.get()
            if response.lower() == 'y':
                ready_clients.add(username)
        return len(ready_clients) == len(self.clients)

    def provide_hint(self, username, question):
        """Provide a hint by eliminating one incorrect option."""
        if username in self.current_hints:
            return
        incorrect_options = [opt for opt in question["options"] if opt[0] != question["answer"]]
        if incorrect_options:
            eliminated = random.choice(incorrect_options)
            self.current_hints[username] = True
            self.scores[username] = max(0, self.scores[username] - 2)  # Penalty for hint
            return {
                "type": MESSAGE_TYPES["hint"],
                "message": f"Eliminated option: {eliminated}",
                "score": self.scores[username]
            }
        return None

    def run_quiz(self):
        """Run the quiz game with new features."""
        while True:
            # Reset hints and select category
            self.current_hints = {}
            self.current_answers = queue.Queue()
            self.select_category()

            # Wait for all players to be ready
            if not self.check_readiness():
                self.broadcast_callback({
                    "type": MESSAGE_TYPES["notification"],
                    "message": "Not all players are ready. Game aborted."
                })
                break

            # Run quiz for selected category
            questions = QUESTIONS[self.selected_category]
            for i, q in enumerate(questions, 1):
                self.current_answers = queue.Queue()
                self.current_hints = {}

                # Broadcast question
                self.broadcast_callback({
                    "type": MESSAGE_TYPES["question"],
                    "number": i,
                    "question": q["question"],
                    "options": q["options"],
                    "difficulty": q["difficulty"],
                    "points": q["points"],
                    "timeout": self.question_timeout
                })

                # Wait for answers
                time.sleep(self.question_timeout)

                # Process answers
                correct_answer = q["answer"]
                results = {}
                while not self.current_answers.empty():
                    username, answer = self.current_answers.get()
                    if answer.upper() == correct_answer:
                        self.scores[username] += q["points"]
                        results[username] = True
                    else:
                        results[username] = False

                # Broadcast results
                self.broadcast_callback({
                    "type": MESSAGE_TYPES["results"],
                    "correct_answer": correct_answer,
                    "scores": self.scores,
                    "individual_results": results
                })

                time.sleep(2)  # Pause between questions

            # Announce final results
            self.broadcast_callback({
                "type": MESSAGE_TYPES["game_over"],
                "scores": self.scores,
                "winner": max(self.scores.items(), key=lambda x: x[1])[0] if self.scores else None
            })

            # Handle rematch voting
            self.current_answers = queue.Queue()
            self.broadcast_callback({
                "type": MESSAGE_TYPES["rematch"],
                "message": "Do you want to play again? (y/n)"
            })
            time.sleep(5)
            rematch_votes = 0
            while not self.current_answers.empty():
                _, vote = self.current_answers.get()
                if vote.lower() == 'y':
                    rematch_votes += 1
            if rematch_votes < len(self.clients):
                break

        self.broadcast_callback({
            "type": MESSAGE_TYPES["notification"],
            "message": "Game session ended."
        })

    def process_answer(self, username, data):
        """Process a client's answer or other input."""
        if self.current_answers:
            if isinstance(data, dict) and data["type"] == MESSAGE_TYPES["hint"]:
                hint_message = self.provide_hint(username, QUESTIONS[self.selected_category][data.get("question_number", 0) - 1])
                if hint_message:
                    # Send hint to specific client
                    if username in self.clients:
                        self.clients[username][0].send(encode_message(hint_message))
            else:
                self.current_answers.put((username, data))