import threading
import socket
from utils.utils import decode_stream, encode_message, MESSAGE_TYPES

class QuizCoordinator:
    def __init__(self, clients, scores, questions, broadcast, timeout, on_quiz_end=None):
        self.clients = clients
        self.scores = scores
        self.questions = questions
        self.broadcast = broadcast
        self.timeout = timeout            # seconds
        self.on_quiz_end   = on_quiz_end
        self.started = False
        self.stopped = False
        self.lock = threading.Lock()

    def start(self):
        with self.lock:
            if self.started:
                return
            self.started = True
        print(f"[Server] Starting quiz for: {list(self.clients.keys())}")
        threading.Thread(target=self.run_quiz, daemon=True).start()

    def stop(self):
        """Signal the quiz to end early."""
        print("[Server] Stopping quiz early.")
        self.stopped = True

    def run_quiz(self):
        for idx, q in enumerate(self.questions, start=1):
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
                                answers[user] = msg["answer"]
                                print(f"[Server] Answer from {user}: {msg['answer']}")
                                return
                except socket.timeout:
                    print(f"[Server] Time up for {user}: no answer received.")
                except Exception as e:
                    print(f"[Server] Error recv from {user}: {e}")
                finally:
                    sock.settimeout(None)  # restore blocking mode

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
            for user, ans in answers.items():
                if ans.strip().lower() == correct.strip().lower():
                    self.scores[user] = self.scores.get(user, 0) + 1
                result["scores"][user] = self.scores.get(user, 0)

            print(f"[Server] Results Q{idx}: {result['scores']}")
            self.broadcast(result)

        # Final game‐over broadcast
        winner = max(self.scores, key=self.scores.get) if self.scores else None
        print(f"[Server] Game over. Winner: {winner}")
        self.broadcast({
            "type": MESSAGE_TYPES["game_over"],
            "winner": winner,
            "scores": self.scores
        })
        for user, sock in self.clients.items():
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
        # reset started/stopped so admin can start a new quiz
        with self.lock:
            self.started = False
            self.stopped = False
