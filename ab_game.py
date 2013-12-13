#!/usr/bin/python

import board
import pente_exceptions

from ab_state import *

CAPTURE_SCORE_BASE = 120 ** 3

class ABGame():
    """ This class acts as a bridge between the AlphaBeta code and my code """
    def __init__(self, base_game):
        s = self.current_state = ABState()
        s.set_state(base_game.current_state)
        self.base_game = base_game

    def to_move(self, state=None):
        if state is None:
            state = self.current_state
        return state.to_move()

    def utility(self, state):
        return state.utility()

    def successors(self, state, depth):
        mn = state.get_move_number()
        if mn == 1:
            # The first black move is always in the centre
            brd_size = self.base_game.get_board().get_size()
            centre_pos = (brd_size/2, brd_size/2)
            p_i = [centre_pos]
        else:
            min_priority = 0
            if depth > 4:
                min_priority = 4

            pos_iter = state.get_iter(state.to_move())
            p_i = pos_iter.get_iter(state.to_move_colour(), min_priority)
        for pos in p_i:
            # create an AB_State for each possible move from state
            succ = state.create_state(pos)
            yield pos, succ

    def terminal_test(self, state):
        return state.terminal()

