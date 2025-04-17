class Scoreboard:
    def __init__(self):
        self.scores = {}

    def get_scores(self):
        return self.scores

    def update_score(self, username, points):
        self.scores[username] = self.scores.get(username, 0) + points