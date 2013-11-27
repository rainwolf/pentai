#!/usr/bin/env python

import unittest
from alpha_beta import *

class MockState(object):
    def __init__(self, name, utility, successors):
        self.name = name
        self.utility = utility
        self.successors = successors

class MockGame:
    def __init__(self, states):
        self.states = dict([(s.name, s) for s in states])
     
    def successors(self, state_name):
        state = self.states[state_name]
        for child_state in state.successors:
            yield child_state

    def utility(self, state_name, player):
        return self.states[state_name].utility

    def terminal_test(self, state_name):
        return len(self.states[state_name].successors) == 0

    def to_move(self, state_name):
        return True # TODO?

class AlphaBetaTest(unittest.TestCase):
    '''
    # TODO: Resurrect
    def test_finished_game(self):
        game = mock.Mock(
            utility=0,
            terminal_test=True,
            to_move=True,
            successors=[("move","child_state")])
        action, value = alphabeta_search(state="start_state", game=game)
        self.assertEquals(action, ("move", "child_state"))
        self.assertEquals(value, 0)
    '''

    def test_top_level_options(self):
        game = MockGame([
            MockState("S0", 1, [(0,"S1"),(1,"S2"),(2,"S3")]),
            MockState("S1", 1, []),
            MockState("S2", 2, []),
            MockState("S3", 1, [])])
        action, value = alphabeta_search(state="S0", game=game)
        self.assertEquals(action, (1, "S2"))
        self.assertEquals(value, 2)

    def test_top_level_with_one_move_having_a_single_descendent(self):
        game = MockGame([
            MockState("S0", 1, [(0,"S1"),(1,"S2"),(2,"S3")]),
            MockState("S1", 1, []),
            MockState("S2", 2, []),
            MockState("S3", 1, [(0,"S4")]),
            MockState("S4", 4, [])])
        action, value = alphabeta_search(state="S0", game=game)
        self.assertEquals(action, (2, "S3"))
        self.assertEquals(value, 4)

    def test_opponent_chooses_bad_move_for_us(self):
        game = MockGame([
            MockState("S0", 1, [(0,"S1"),(1,"S2")]),
            MockState("S1", 1, [(0,"S3"),(1,"S4")]),
            MockState("S2", 2, []),
            MockState("S3", 3, []),
            MockState("S4", 4, [])])
        action, value = alphabeta_search(state="S0", game=game)
        self.assertEquals(action, (0, "S1"))
        self.assertEquals(value, 3)

    def test_only_search_one_depth_level(self):
        game = MockGame([
            MockState("S0", 0, [(0,"S1")]),
            MockState("S1", 1, [(0,"S2")]),
            MockState("S2", 2, [(0,"S3")]),
            MockState("S3", 3, [])])
        action, value = alphabeta_search(state="S0", max_depth=1, game=game)
        self.assertEquals(value, 1)

    def test_only_search_two_depth_levels(self):
        game = MockGame([
            MockState("S0", 0, [(0,"S1")]),
            MockState("S1", 1, [(0,"S2")]),
            MockState("S2", 2, [(0,"S3")]),
            MockState("S3", 3, [])])
        action, value = alphabeta_search(state="S0", max_depth=2, game=game)
        self.assertEquals(value, 2)

    def test_terminal_state(self):
        game = MockGame([
            MockState("S0", 0, [(0,"S1")]),
            MockState("S1", 1, [(0,"S2")]),
            MockState("S2", 2, [(0,"S3")]),
            MockState("S3", 3, [])])
        action, value = alphabeta_search(state="S0", max_depth=4, game=game)
        self.assertEquals(value, 3)

if __name__ == "__main__":
    unittest.main()



