import threading
import socket
import time
import random
from utils.utils import decode_stream, encode_message, MESSAGE_TYPES

class QuizCoordinator:
    def __init__(self, clients, scores, questions, broadcast, timeout, on_quiz_end=None):
        self.clients = clients
        self.scores = scores
        self.questions = questions
        self.broadcast = broadcast
        self.timeout = timeout
        self.on_quiz_end = on_quiz_end
        self.started = False
        self.stopped = False
        self.lock = threading.Lock()
        self.answer_timestamps = {}  # user -> last correct answer timestamp
        self.numQuestions = 10

    def start(self):
        with self.lock:
            if self.started:
                return
            self.started = True
        print(f"[Server] Starting quiz for: {list(self.clients.keys())}")
        threading.Thread(target=self.run_quiz, daemon=True).start()

    def stop(self):
        print("[Server] Stopping quiz early.")
        self.stopped = True

    def run_quiz(self):
        all_questions = self.questions 
        selected_questions = random.sample(all_questions, self.numQuestions)
        for idx, q in enumerate(selected_questions, start=1):
            if self.stopped:
                break

            print(f"[Server] Q{idx}: {q['question']}")
            self.broadcast({
                "type": MESSAGE_TYPES["question"],
                "number": idx,
                "question": q["question"],
                "options": q["options"],
                "timeout": self.timeout
            })

            answers = {}
            threads = []

            def collect(user, sock):
                sock.settimeout(self.timeout)
                buf = ""
                try:
                    while True:
                        chunk = sock.recv(1024).decode()
                        if not chunk or self.stopped:
                            return
                        buf += chunk
                        for msg, buf in decode_stream(buf):
                            if msg.get("type") == MESSAGE_TYPES["answer"]:
                                ans = msg.get("answer", "").strip()
                                ts = msg.get("timestamp", time.time())
                                answers[user] = {"answer": ans, "timestamp": ts}
                                print(f"[Server] Answer from {user}: {ans} at {ts}")
                                return
                except socket.timeout:
                    print(f"[Server] Time up for {user}: no answer received.")
                except Exception as e:
                    print(f"[Server] Error recv from {user}: {e}")
                finally:
                    sock.settimeout(None)

            for user, sock in list(self.clients.items()):
                t = threading.Thread(target=collect, args=(user, sock), daemon=True)
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            if self.stopped:
                break

            correct = q["answer"]
            print(f"[Server] Correct Q{idx}: {correct}")
            result = {
                "type": MESSAGE_TYPES["result"],
                "number": idx,
                "correct": correct,
                "scores": {}
            }

            for user, record in answers.items():
                ans = record["answer"]
                ts = record["timestamp"]
                if ans.lower() == correct.lower():
                    self.scores[user] = self.scores.get(user, 0) + 1
                    self.answer_timestamps[user] = ts
                else:
                    self.scores[user] = self.scores.get(user, 0) - 0.5
                result["scores"][user] = self.scores[user]

            print(f"[Server] Results Q{idx}: {result['scores']}")
            self.broadcast(result)

        # Determine winner with tie-breaking
        winner = None
        if self.scores:
            sorted_players = sorted(
                self.scores.items(),
                key=lambda item: (-item[1], self.answer_timestamps.get(item[0], float("inf")))
            )
            winner = sorted_players[0][0]
        print(f"[Server] Game over. Winner: {winner}")

        self.broadcast({
            "type": MESSAGE_TYPES["game_over"],
            "winner": winner,
            "scores": self.scores
        })

        for user, sock in list(self.clients.items()):
            try:
                sock.send(encode_message({
                    "type": MESSAGE_TYPES["notification"],
                    "message": "Quiz has ended. You are back in the lobby."
                }))
                sock.send(encode_message({
                    "type": MESSAGE_TYPES["lobby"],
                    "message": "Waiting for the next quiz to start..."
                }))
            except:
                pass

        if self.on_quiz_end:
            self.on_quiz_end()

        with self.lock:
            self.started = False
            self.stopped = False
