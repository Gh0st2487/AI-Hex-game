from trueskill import Rating
from random import Random

class BasePlayer(object):

    def __init__(self, name, seed=None, color=None):
        self.name = name
        self.color = color
        self.board = None
        self.rating = Rating()
        self.rating_history = [self.rating]
        self.games_played = 0
        self.games_won = 0
        self.local_random = Random(seed)
        self.eval_count = 0
        self.turn_count = 0
        self.turn_time = 0
        self.tt_hits_full = 0
        self.tt_hits_half = 0

    def reset(self):
        pass

    def set_seed(self, seed):
        self.local_random = Random(seed)

    def set_board_and_color(self, board, color):
        self.board = board
        self.color = color

    def set_rating(self, rating):
        self.rating_history.append(rating)
        self.rating = rating

    def do_turn(self, verbose=0):
        raise NotImplementedError("Abstract method, please subclass")