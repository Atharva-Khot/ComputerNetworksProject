import threading
import time
from utils import MESSAGE_TYPES

class UserInterface:
    def __init__(self, send_callback):
        self.send_callback = send_callback

    def handle_answer(self, timeout, question_number):
        """Handle user answer input with timeout."""
        start_time = time.time()
        answer = input("\nYour answer (A/B/C/D or 'hint'): ").strip().upper()

        if time.time() - start_time <= timeout:
            if answer == "HINT":
                self.send_callback({
                    "type": MESSAGE_TYPES["hint"],
                    "question_number": question_number
                })
            elif answer in ['A', 'B', 'C', 'D']:
                self.send_callback({
                    "type": MESSAGE_TYPES["answer"],
                    "answer": answer
                })

    def start_answer_thread(self, timeout, question_number):
        """Start a thread to handle answer input."""
        threading.Thread(
            target=self.handle_answer,
            args=(timeout, question_number),
            daemon=True
        ).start()