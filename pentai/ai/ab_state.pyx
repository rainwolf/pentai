import pentai.base.game_state as gs_m
import pentai.base.game as g_m
from pentai.base.defines import *
import pentai.base.gs_observer as gso_m
import pentai.ai.utility_stats as us_m

class ABState(gso_m.GSObserver):
    """ Bridge for state, for use by alpha_beta code """
    def __init__(self, parent=None, search_filter=None,
            utility_calculator=None):
        if parent == None:
            assert search_filter != None
            self.utility_stats = us_m.UtilityStats(search_filter=search_filter)
        else:
            self.utility_stats = us_m.UtilityStats(parent=parent.utility_stats)
        if utility_calculator != None:
            self.utility_calculator = utility_calculator
        else:
            assert parent != None
            self.utility_calculator = parent.utility_calculator
        self.seen = set()

    def clean_up(self):
        self.state.remove_observer(self)

    def get_utility_stats(self):
        return self.utility_stats

    def get_takes(self):
        return self.utility_stats.takes

    def get_threats(self):
        return self.utility_stats.threats

    def get_iter(self, to_move):
        return self.utility_stats.search_filter

    def get_captured(self, colour):
        return self.state.get_all_captured()[colour]

    def set_state(self, s):
        self.state = s
        # TODO: this should only need to be set once - it's referenced
        # by all states in a particular game
        self.utility_calculator.set_rules(s.get_rules())
        s.add_observer(self)

    def to_move_colour(self):
        return self.state.to_move_colour()

    def get_move_number(self):
        return self.state.get_move_number()

    def to_move(self):
        """ This is only to keep the AB code unchanged; the value is unused. """
        return None

    def search_player_colour(self):
        """ The AI player who is performing the search """
        game = self.game()
        return game.to_move_colour()

    def is_our_turn(self):
        return (self.to_move_colour() == self.search_player_colour())

    def __repr__(self):
        ret = "%s. %s Captures: %s" % \
                (self.get_move_number(),
                 self.utility_stats,
                 self.state.get_all_captured())
        return ret

    def game(self):
        return self.state.game

    def get_state(self):
        return self.state

    def history_string(self):
        """ For debugging only """
        hist_str = ""
        ab_s = self
        # TODO: Just make it go back to the start?
        cs = self.state.game.current_state
        while ab_s.state != cs:
            hist_str = str(ab_s.state) + "\n" + hist_str
            ab_s = ab_s.parent
        return hist_str

    def utility(self):
        return self.utility_calculator.utility(self, self.utility_stats)

    # TODO: Rename to get_board
    def board(self):
        return self.state.board

    def is_illegal(self, pos):
        return self.state.is_illegal(pos)

    def get_rules(self):
        return self.game().rules

    def set_won_by(self, colour):
        self.state.set_won_by(colour)

    def reset_state(self, game):
        self.utility_stats.reset()

    # TODO: Could these two be moved to utility_stats too?
    def before_set_occ(self, game, pos, colour):
        self.utility_stats.before_set_occ(game, pos, colour, self.board(), self.get_rules())

    def after_set_occ(self, game, pos, colour):
        self.utility_stats.after_set_occ(game, pos, colour, self.board(), self.get_rules())

    def create_state(self, move_pos):
        ab_child = ABState(self)

        # clone the base level state object
        base_child = gs_m.GameState(self.state.game, self.state)

        # connect the two (including move hook)
        ab_child.set_state(base_child)

        # make the move for the base (which updates ab_child)
        base_child.make_move(move_pos)

        return ab_child

    def set_seen(self, seen):
        self.seen = seen

    def get_seen(self):
        return self.seen

    def terminal(self):
        return self.state.get_won_by() != EMPTY

