import threading
from utils.utils import decode_stream, encode_message, MESSAGE_TYPES

class QuizCoordinator:
    def __init__(self, clients, scores, questions, broadcast):
        self.clients = clients            # dict: username -> socket
        self.scores = scores              # dict: username -> int
        self.questions = questions        # list of question dicts
        self.broadcast = broadcast        # function to send to all

    def run_quiz(self):
        for q in self.questions:
            # Broadcast question
            self.broadcast({
                "type": MESSAGE_TYPES["question"],
                "question": q["question"],
                "options": q["options"]
            })

            # Collect answers
            answers = {}
            for username, sock in list(self.clients.items()):
                buffer = ""
                try:
                    while True:
                        data = sock.recv(1024).decode()
                        if not data:
                            break
                        buffer += data
                        for msg, buffer in decode_stream(buffer):
                            if msg.get("type") == MESSAGE_TYPES["answer"]:
                                answers[username] = msg.get("answer")
                                raise StopIteration
                except StopIteration:
                    pass
                except Exception:
                    continue

            # Evaluate and broadcast results
            correct = q["answer"]
            result_msg = {
                "type": MESSAGE_TYPES["result"],
                "correct": correct,
                "scores": {}
            }
            for username, ans in answers.items():
                if ans.strip().lower() == correct.strip().lower():
                    self.scores[username] = self.scores.get(username, 0) + 1
                result_msg["scores"][username] = self.scores.get(username, 0)

            self.broadcast(result_msg)

        # Game over
        winner = max(self.scores, key=self.scores.get)
        self.broadcast({
            "type": MESSAGE_TYPES["game_over"],
            "winner": winner,
            "scores": self.scores
        })