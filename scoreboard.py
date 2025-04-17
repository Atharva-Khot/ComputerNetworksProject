class Scoreboard:
    def __init__(self):
        self.scores = {}

    def add_player(self, username):
        """Add a player to the scoreboard."""
        self.scores[username] = 0

    def update_score(self, username, points):
        """Update a player's score."""
        if username in self.scores:
            self.scores[username] += points

    def get_scores(self):
        """Get the current scores."""
        return self.scores