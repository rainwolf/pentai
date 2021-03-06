from pentai.base.game import *
import pentai.base.rules as r_m

from persistent import Persistent

class PreservedGame(Persistent):
    def __init__(self, game=None, *args, **kwargs):
        super(PreservedGame, self).__init__(*args, **kwargs)
        if game:
            self.game_id = game.game_id
            self.rules = game.rules.key()
            self.date = game.get_date()
            self.won_by = game.get_won_by()
            p1 = game.get_player(1)
            p2 = game.get_player(2)
            self.players = (None, p1.get_key(), p2.get_key())
            #self.ratings = (None, p1.get_rating(), p2.get_rating())
            self.ratings = (None, game.get_rating(P1),
                                  game.get_rating(P2))
            self.moves = tuple(game.move_history)
            self.times = tuple(game.time_history)
            self.resume_move_number = game.resume_move_number

    def key(self):
        return self.game_id

    def get_date(self):
        return self.date

    def get_size(self):
        return self.rules[0]

    def get_rules_type_name(self):
        return r_m.get_type_name(self.rules[1])

    def get_won_by(self):
        try:
            return self.won_by
        except AttributeError:
            return

    def __eq__(self, other):
        return self.key() == other.key()

    def get_player_id(self, colour):
        return self.players[colour]

    def get_rating(self, colour):
        try:
            return self.ratings[colour]
        except AttributeError:
            return 1

    def get_size(self):
        return self.rules[0]

    '''
    # TODO?
    def rating_factor(self, colour):
        return max(self.max_depth-3, 0)
    '''

    def restore(self, pm, update_cache=True):
        p1 = pm.find(self.players[1], update_cache)
        p2 = pm.find(self.players[2], update_cache)
        orig_game = Game(r_m.Rules(*self.rules), p1, p2)
        orig_game.game_id = self.game_id
        orig_game.date = self.date

        orig_game.move_history = list(self.moves)
        try:
            orig_game.time_history = list(self.times)
        except AttributeError:
            orig_game.time_history = [0] * (len(self.moves) + 2)
        try:
            orig_game.resume_move_number = self.resume_move_number
        except AttributeError:
            orig_game.resume_move_number = None

        return orig_game
