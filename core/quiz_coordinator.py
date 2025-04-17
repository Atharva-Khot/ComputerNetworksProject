import threading
from utils.utils import decode_stream, encode_message, MESSAGE_TYPES

class QuizCoordinator:
    def __init__(self, clients, scores, questions, broadcast):
        self.clients = clients            # dict: username -> socket
        self.scores = scores              # dict: username -> int
        self.questions = questions        # list of question dicts
        self.broadcast = broadcast        # function to send to all
        self.started = False
        self.lock = threading.Lock()

    def start(self):
        """Start the quiz exactly once."""
        with self.lock:
            if self.started:
                return
            self.started = True
        print("[Server] Quiz starting with players:", list(self.clients.keys()))
        threading.Thread(target=self.run_quiz, daemon=True).start()

    def run_quiz(self):
        for idx, q in enumerate(self.questions, start=1):
            # 1) Broadcast the question
            print(f"[Server] Broadcasting Q{idx}: {q['question']}")
            self.broadcast({
                "type": MESSAGE_TYPES["question"],
                "number": idx,
                "question": q["question"],
                "options": q["options"]
            })

            # 2) Spin up one thread per client to collect answers in parallel
            answers = {}
            threads = []

            def collect_answer(username, sock):
                buffer = ""
                try:
                    while True:
                        chunk = sock.recv(1024).decode()
                        if not chunk:
                            break
                        buffer += chunk
                        for msg, buffer in decode_stream(buffer):
                            if msg.get("type") == MESSAGE_TYPES["answer"]:
                                answers[username] = msg["answer"]
                                print(f"[Server] Got {username} → {msg['answer']}")
                                return
                except Exception as e:
                    print(f"[Server] Error collecting from {username}: {e}")

            for user, sock in list(self.clients.items()):
                t = threading.Thread(target=collect_answer, args=(user, sock), daemon=True)
                t.start()
                threads.append(t)

            # 3) Wait for all to finish
            for t in threads:
                t.join()

            # 4) Score & broadcast results
            correct = q["answer"]
            print(f"[Server] Correct for Q{idx}: {correct}")

            result_msg = {
                "type": MESSAGE_TYPES["result"],
                "number": idx,
                "correct": correct,
                "scores": {}
            }
            for user, ans in answers.items():
                if ans.strip().lower() == correct.strip().lower():
                    self.scores[user] = self.scores.get(user, 0) + 1
                result_msg["scores"][user] = self.scores.get(user, 0)

            print(f"[Server] Broadcasting results Q{idx}: {result_msg['scores']}")
            self.broadcast(result_msg)

        # 5) Finally, game over
        winner = max(self.scores, key=self.scores.get) if self.scores else None
        print(f"[Server] Game over. Winner: {winner}")
        self.broadcast({
            "type": MESSAGE_TYPES["game_over"],
            "winner": winner,
            "scores": self.scores
        })