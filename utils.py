import json

# Message types
MESSAGE_TYPES = {
    "welcome": "welcome",
    "username": "username",
    "question": "question",
    "answer": "answer",
    "results": "results",
    "game_over": "game_over",
    "notification": "notification",
    "error": "error",
    "ready": "ready",
    "category": "category",
    "hint": "hint",
    "rematch": "rematch"
}

# Quiz questions with categories and difficulty
QUESTIONS = {
    "History": [
        {"question": "Who was the first president of the USA?", "options": ["A. Lincoln", "B. Washington", "C. Jefferson", "D. Adams"], "answer": "B", "difficulty": "Easy", "points": 5},
        {"question": "In which year did World War II end?", "options": ["A. 1943", "B. 1944", "C. 1945", "D. 1946"], "answer": "C", "difficulty": "Medium", "points": 10}
    ],
    "Science": [
        {"question": "Which planet is known as the Red Planet?", "options": ["A. Jupiter", "B. Mars", "C. Venus", "D. Mercury"], "answer": "B", "difficulty": "Easy", "points": 5},
        {"question": "What gas do plants absorb from the atmosphere?", "options": ["A. Oxygen", "B. Nitrogen", "C. Carbon Dioxide", "D. Helium"], "answer": "C", "difficulty": "Medium", "points": 10}
    ],
    "Math": [
        {"question": "What is 2 + 2?", "options": ["A. 3", "B. 4", "C. 5", "D. 6"], "answer": "B", "difficulty": "Easy", "points": 5},
        {"question": "What is the square root of 16?", "options": ["A. 2", "B. 4", "C. 8", "D. 16"], "answer": "B", "difficulty": "Hard", "points": 15}
    ]
}

def encode_message(message):
    """Encode a message to JSON string."""
    return json.dumps(message).encode()

def decode_message(data):
    """Decode a JSON string to a Python dictionary."""
    return json.loads(data.decode())