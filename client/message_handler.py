import threading, sys
import time
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

        # elif t == MESSAGE_TYPES["lobby"]:
        #     self.ui.display_lobby(msg.get("message"))
        #     self.in_lobby = True

        elif t == MESSAGE_TYPES["notification"]:
            self.ui.display_notification(msg.get("message"))

        elif t == MESSAGE_TYPES["question"]:
            timeout = msg.get("timeout", 15)
            print(f"\nQuestion {msg['number']}: {msg['question']} (you have {timeout}s)")
            for opt in msg["options"]:
                print(f"- {opt}")

            # start a thread to get answer with timeout
            threading.Thread(
                target=self._get_answer_with_timeout,
                args=(timeout,),
                daemon=True
            ).start()
        elif t == MESSAGE_TYPES["result"]:
            self.ui.display_result(msg)

        elif t == MESSAGE_TYPES["game_over"]:
            self.ui.display_game_over(msg)
            # no exit() or should_exit flag here:
            print("\n[Client] Quiz ended—returning to lobby.")
            # next we expect a 'lobby' message
            return

        elif t == MESSAGE_TYPES["lobby"]:
            self.ui.display_lobby(msg.get("message"))
            # stay connected; just wait for the next question
            return


        elif t == MESSAGE_TYPES["error"]:
            self.ui.display_error(msg.get("message"))
            
    def _get_answer_with_timeout(self, timeout):
            answer = [None]
            stop_event = threading.Event()

            # 1) Ticker thread
            def ticker():
                for i in range(timeout, 0, -1):
                    if stop_event.is_set():
                        return
                    # Move up and overwrite the countdown line
                    sys.stdout.write(f"\033[F\rCountdown: {i:2d} seconds remaining\n")
                    sys.stdout.flush()
                    time.sleep(1)
                sys.stdout.write("\033[F\rTime's up!                     \n")
                sys.stdout.flush()
                stop_event.set()

            def reader():
                print(" ", end='', flush=True)
                answer[0] = input()
                stop_event.set()

            # Print the two lines first
            print("Countdown: -- seconds remaining")
            print(" ", end='', flush=True)

            # Start threads
            t_tick = threading.Thread(target=ticker, daemon=True)
            t_read = threading.Thread(target=reader, daemon=True)

            t_tick.start()
            t_read.start()

            t_read.join(timeout)
            stop_event.set()

            # t_tick = threading.Thread(target=ticker, daemon=True)
            # t_read = threading.Thread(target=reader, daemon=True)

            # t_tick.start()
            # t_read.start()

            # # Wait for either the reader or the timeout
            # t_read.join(timeout)
            # stop_event.set()     # signal ticker to stop (if it's still running)

            # If reader is still alive, it means timeout hit first
            if t_read.is_alive():
                print("\n[Client] No answer submitted.")
                self.send({ 
                    "type": MESSAGE_TYPES["answer"], 
                    "answer": "",
                    "timestamp" : time.time() 
                })
            else:
                self.send({ 
                    "type": MESSAGE_TYPES["answer"], 
                    "answer": answer[0],
                    "timestamp" : time.time()
                })