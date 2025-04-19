# 🎮 Multiplayer Quiz Game using TCP Sockets

A terminal-based multiplayer quiz game built in Python using **TCP sockets**. Designed as a **Computer Networks course project**, this system showcases advanced networking concepts including custom protocols, multithreading, lobby management, timers, and administrative controls.

---

## 📦 Features

### 🔌 Networking
- **TCP socket communication** between server and clients.
- **Custom message protocol** using JSON with newline delimiters.
- **Thread-per-client** server architecture and non-blocking I/O alternatives.
- **Socket option tuning** (e.g., timeouts) for per-player timers.

### 🧠 Game Logic
- Real-time **multiplayer quiz** with score tracking.
- **Automatic score calculation** and live result broadcasts.
- **Per-player question timers**: configurable `QUESTION_TIMEOUT` in `config.py`.
- **Client-side countdown** display, auto-submission on timeout.
- Server logs timeouts: "Time up for {user}" messages.

### 🧍 Lobby System
- **Waiting Lobby**: new players join here until quiz starts.
- **Active Lobby**: players moved here when server admin runs `start`.
- **Automatic return to lobby** after quiz ends (natural or admin-ended).

### 🛠 Server Admin Commands
| Command             | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `i`                 | Show all waiting and active players.                                        |
| `start`             | Move everyone from waiting to active lobby and begin the quiz.              |
| `end game`          | End the current quiz immediately; players return to waiting lobby.          |
| `kick <username>`   | Remove a player from whichever lobby they are in.                           |
| `block <username>`  | Permanently block a user from joining this session.                         |
| `exit`              | Gracefully shut down the server and disconnect all clients.                 |

---

## 📁 Project Structure

```
quiz_game/
├── README.md
├── config.py                # HOST, PORT, QUESTION_TIMEOUT
├── utils/
│   ├── __init__.py
│   ├── utils.py             # encode/decode, load questions, constants
│   └── questions.json       # Quiz question data
├── networking/
│   ├── __init__.py
│   ├── server_connection.py # Server socket binding and accept
│   └── client_connection.py # Client connect, send, receive
├── core/
│   ├── __init__.py
│   ├── scoreboard.py        # Score tracking
│   └── quiz_coordinator.py  # Quiz flow, timers, natural end callback
├── server/
│   ├── __init__.py
│   ├── client_handler.py    # Handshake, lobby join, and notifications
│   └── server.py            # Entry-point, admin console, lobbies
└── client/
    ├── __init__.py
    ├── client.py            # Entry-point, receive loop
    ├── message_handler.py   # Process messages, start timers
    └── user_interface.py    # CLI prompts and displays
```

---

## 📖 Configuration (`config.py`)
```python
HOST = 'localhost'
PORT = 12345
# Seconds each player has to answer a question\QUESTION_TIMEOUT = 15
```

---

## 🧪 Sample `utils/questions.json`
```json
[
  {
    "question": "What is the capital of France?",
    "options": ["A) Paris", "B) London", "C) Rome", "D) Berlin"],
    "answer": "A"
  },
  {
    "question": "Which planet is known as the Red Planet?",
    "options": ["A) Earth", "B) Mars", "C) Jupiter", "D) Saturn"],
    "answer": "B"
  }
]
```

---

## 🧠 Concepts Demonstrated

- **TCP Communication & Threading**: concurrent client handling.
- **Custom Protocol**: JSON framing with delimiters.
- **Per-Player Timers**: socket timeouts and client countdowns.
- **Lobby Management**: waiting vs active states, callback-driven transitions.
- **Administrative Controls**: runtime commands to inspect, kick, block, and terminate.
- **Graceful Shutdown**: clean exit preserving state and notifying clients.

---

## 📋 Requirements

- Python 3.6 or higher. No external libraries required.

---

## 🚀 How to Run

1. **Clone and enter project**:
   ```bash
   cd quiz_game
   ```
2. **Start the server** (from project root):
   ```bash
   python3 -m server.server
   ```
3. **Start clients** in separate terminals:
   ```bash
   python3 -m client.client
   ```
4. **Server Admin** commands:
   - `i`         : show current lobby info
   - `start`     : move to active lobby & begin quiz
   - `end game`  : abort quiz, return players to waiting
   - `kick user` : remove a player
   - `block user`: disallow future joins
   - `exit`      : shut down everything

---

## 🔭 Future Enhancements

- Implement **select/epoll**-based server to replace threads.
- Add **chat** or **buzz** features over TCP.
- Integrate **TLS encryption** for secure transport.
- Persist **leaderboards** to a database or file.
- Build a **web interface** with WebSockets for richer UI.

---