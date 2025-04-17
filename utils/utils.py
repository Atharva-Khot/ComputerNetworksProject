import json

DELIMITER = "\n"

MESSAGE_TYPES = {
    "welcome": "welcome",
    "username": "username",
    "lobby": "lobby",
    "notification": "notification",
    "question": "question",
    "answer": "answer",
    "result": "result",
    "game_over": "game_over",
    "error": "error"
}


def encode_message(msg):
    """Encode a dict to JSON bytes appended with delimiter."""
    return (json.dumps(msg) + DELIMITER).encode()


def decode_stream(buffer):
    """Generator yielding (message_dict, rest_buffer) pairs."""
    while DELIMITER in buffer:
        raw, buffer = buffer.split(DELIMITER, 1)
        yield json.loads(raw), buffer
    return


def load_questions():
    """Load quiz questions from questions.json."""
    with open('utils/questions.json', 'r') as f:
        return json.load(f)