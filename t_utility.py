#!/usr/bin/env python

import unittest

from length_counter import *
from ab_bridge import *
from player import *
import game_state
from board import *
from mock import *

import pdb

inf = alpha_beta.infinity / 2

class UtilityTest(unittest.TestCase):
    def setUp(self):
        self.s = ABState()
        self.captured = [0, 0, 0]
        self.set_search_player_colour(BLACK)
        self.black_player = Player("Black Name", BLACK)
        self.white_player = Player("White Name", WHITE)

    def set_captured(self, black_captures, white_captures):
        self.captured[BLACK] = black_captures
        self.captured[WHITE] = white_captures

    def set_search_player_colour(self, search_player_colour):
        self.to_move_colour = BLACK
        self.game = Mock({"to_move_colour":search_player_colour})
        self.gs = Mock( {"add_observer": None, "get_all_captured": self.captured}) 
        self.gs.board = Board(13)
        self.s.set_state(self.gs)
        self.gs.game = self.game
        
    def test_utility_single_stone_better_than_none(self):
        self.s.black_lines = LengthCounter([20,0,0,0,0])
        self.s.white_lines = LengthCounter([0,0,0,0,0])
        u = self.s.utility(self.black_player)
        self.assertGreater(u, 0)

    def test_utility_more_singles_is_better(self):
        self.s.black_lines = LengthCounter([1,0,0,0,0])
        self.s.white_lines = LengthCounter([0,0,0,0,0])
        u = self.s.utility(self.black_player)
        self.assertGreater(u, 0)

    def test_utility_more_twos_is_better(self):
        self.s.black_lines = LengthCounter([0,1,0,0,0])
        self.s.white_lines = LengthCounter([0,0,0,0,0])
        u = self.s.utility(self.black_player)
        self.assertGreater(u, 0)

    def test_utility_more_threes_is_better(self):
        self.s.black_lines = LengthCounter([0,0,1,0,0])
        self.s.white_lines = LengthCounter([0,0,0,0,0])
        u = self.s.utility(self.black_player)
        self.assertGreater(u, 0)

    def test_utility_more_fours_is_better(self):
        self.s.black_lines = LengthCounter([0,0,0,1,0])
        self.s.white_lines = LengthCounter([0,0,0,0,0])
        u = self.s.utility(self.black_player)
        self.assertGreater(u, 0)

    def test_utility_less_ones_is_worse(self):
        self.s.black_lines = LengthCounter([0,0,0,0,0])
        self.s.white_lines = LengthCounter([1,0,0,0,0])
        u = self.s.utility(self.black_player)
        self.assertLess(u, 0)

    def test_utility_less_ones_is_worse(self):
        self.s.black_lines = LengthCounter([0,0,0,0,0])
        self.s.white_lines = LengthCounter([1,0,0,0,0])
        u = self.s.utility(self.black_player)
        self.assertLess(u, 0)

    def test_utility_five_is_a_win(self):
        self.s.black_lines = LengthCounter([0,0,0,0,1])
        self.s.white_lines = LengthCounter([99,99,99,99,0])
        u = self.s.utility(self.black_player)
        self.assertGreaterEqual(u, inf)

    def test_black_win_by_captures(self):
        self.s.black_lines = LengthCounter([0,0,0,0,0])
        self.s.white_lines = LengthCounter([0,0,0,0,0])
        self.set_captured(10, 0)
        u = self.s.utility(self.black_player)
        self.assertGreaterEqual(u, inf)

    def test_white_win_by_captures(self):
        self.s.black_lines = LengthCounter([0,0,0,0,0])
        self.s.white_lines = LengthCounter([0,0,0,0,0])
        self.set_captured(0, 10)
        u = self.s.utility(self.black_player)
        self.assertLessEqual(u, -inf)

    def test_one_capture_worth_more_than_a_three(self):
        self.s.black_lines = LengthCounter([0,0,0,0,0])
        self.s.white_lines = LengthCounter([0,0,1,0,0])
        self.set_captured(1, 0)
        u = self.s.utility(self.black_player)
        self.assertGreaterEqual(u, 0)

    def test_one_capture_worth_less_than_a_four(self):
        #pdb.set_trace()
        self.s.black_lines = LengthCounter([0,0,0,0,0])
        self.s.white_lines = LengthCounter([0,0,0,1,0])
        self.set_captured(1, 0)
        u = self.s.utility(self.black_player)
        self.assertLessEqual(u, 0)

    ######################

    def test_white_search(self):
        """ Search by white """
        #pdb.set_trace()
        self.set_search_player_colour(WHITE)
        self.s.black_lines = LengthCounter([0,0,0,0,0])
        self.s.white_lines = LengthCounter([0,0,1,0,0])
        u = self.s.utility(self.white_player)
        self.assertGreaterEqual(u, 0)

    def test_white_capture(self):
        """ Search by white """
        #pdb.set_trace()
        self.set_search_player_colour(WHITE)
        self.s.black_lines = LengthCounter([0,0,0,0,0])
        self.s.white_lines = LengthCounter([0,0,0,0,0])
        self.set_captured(0, 1)
        u = self.s.utility(self.white_player)
        self.assertGreaterEqual(u, 0)

    def test_black_to_move_advantage(self):
        """ Search by white """
        self.set_search_player_colour(WHITE)
        self.s.black_lines = LengthCounter([1,0,0,0,0])
        self.s.white_lines = LengthCounter([1,0,0,0,0])
        u = self.s.utility(self.white_player)
        self.assertLessEqual(u, 0)

    '''
    # I need to think about this...
    def test_depth_turn_doesnt_invert_score(self):
        """ Search by white """
        self.set_search_player_colour(WHITE)
        self.s.black_lines = LengthCounter([1,0,0,0,0])
        self.s.white_lines = LengthCounter([1,0,0,0,0])
        u = self.s.utility(self.black_player)
        self.assertLessEqual(u, 0)
    '''

if __name__ == "__main__":
    unittest.main()



