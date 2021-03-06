#!/usr/bin/env python

import unittest

from pentai.base.board import *
from pentai.ai.priority_filter_2 import *

class PriorityFilter2Test(unittest.TestCase):
    def setUp(self):
        self.pf2 = PriorityFilter2()

    def arc(self, colour, length, candidate_list, inc=1):
        self.pf2.add_or_remove_candidates(colour, length, candidate_list, inc)

    def set_captured_by(self, colour, captured):
        self.pf2.captured[colour] = captured

    def ar_take(self, *args, **kwargs):
        self.pf2.add_or_remove_take(*args, **kwargs)

    def ar_threat(self, *args, **kwargs):
        self.pf2.add_or_remove_threat(*args, **kwargs)

    def test_dont_start_in_the_middle_13(self):
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 0)

    def test_add_and_remove(self):
        self.arc(P1, 4, ((3,4),))
        self.arc(P1, 4, ((3,4),), -1)
        self.arc(P1, 3, ((3,2),))
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 1)
        self.assertEquals(l[0],(3,2))

    def test_iterate_over_our_four(self):
        self.arc(P1, 4, ((3,4),))
        self.arc(P1, 3, ((3,2),))
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 1)
        self.assertEquals(l[0],(3,4))

    def test_iterate_over_one_of_their_fours(self):
        self.arc(P2, 4, ((3,4),))
        self.ar_take(P1, (3,2))
        self.set_captured_by(P1, 6)
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 2)
        self.assertEquals(l[0],(3,4))
        self.assertEquals(l[1],(3,2))

    def test_two_of_their_fours_try_the_take(self):
        self.arc(P2, 4, ((1,2),))
        self.arc(P2, 4, ((3,4),))
        self.ar_take(P1, (3,2))
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 1)
        self.assertEquals(l[0],(3,2))

    def test_two_of_their_fours_no_take(self):
        #st()
        self.arc(P2, 4, ((1,2),))
        self.arc(P2, 4, ((3,4),))
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 1)
        # It doesn't matter which one we choose, we're lost
        # Evaluating this node should give the result
        # But we need to choose one or the other

    def test_finish_capture_win(self):
        self.set_captured_by(P1, 8)
        self.ar_take(P1, (1,2))
        self.arc(P2, 4, ((3,4),))
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 1)
        self.assertEquals(l[0],(1,2))

    def test_block_or_take_to_defend_capture_loss(self):
        self.set_captured_by(P2, 8)
        self.ar_take(P1, (1,2))
        self.ar_take(P2, (3,4))
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 2)

    def test_iterate_over_own_black_first(self):
        self.arc(P2, 4, ((1,5),))
        self.arc(P1, 4, ((3,4),))
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 1)
        self.assertEquals(l[0],(3,4))

    def test_iterate_over_higher_priority_only(self):
        self.arc(P2, 3, ((1,5),))
        self.arc(P2, 4, ((3,4),))
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 1)
        self.assertEquals(l[0],(3,4))

    def test_iterate_over_capture(self):
        self.pf2.add_or_remove_take(P1, (3,4))
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 1)
        self.assertEquals(l[0],(3,4))

    def test_iterate_over_own_capture_first(self):
        self.pf2.add_or_remove_take(P1, (1,2))
        self.pf2.add_or_remove_take(P2, (3,4))
        l = list(self.pf2.get_iter(P2))
        self.assertEquals(len(l), 2)
        self.assertEquals(l[0],(3,4))
        self.assertEquals(l[1],(1,2))

    def test_iterate_over_other_players_four_before_our_capture(self):
        self.pf2.add_or_remove_take(P2, (7,2))
        self.arc(P1, 4, ((3,4),))
        l = list(self.pf2.get_iter(P2))
        self.assertEquals(len(l), 2)
        self.assertEquals(l[0],(3,4))
        self.assertEquals(l[1],(7,2))

    def atest_iterate_over_other_players_capture_before_our_threes(self):
        self.arc(P1, 3, ((3,4),(1,5)))
        self.pf2.add_or_remove_take(P2, (7,2))
        l = list(self.pf2.get_iter(P2))
        self.assertEquals(len(l), 3)
        self.assertEquals(l[0],(7,2))
        our_threes = ((3,4),(1,5))
        self.assertIn(l[1], our_threes)
        self.assertIn(l[2], our_threes)

    def test_iterate_block_only(self):
        self.arc(P2, 3, ((1,5),(2,4)))
        self.pf2.add_or_remove_take(P1, (1,5))
        self.arc(P1, 4, ((2,4),))
        l = list(self.pf2.get_iter(P2))
        self.assertEquals(len(l), 1)
        self.assertEquals(l[0],(2,4))

    def test_iterate_over_capture(self):
        self.pf2.add_or_remove_take(P1, (1,5))
        l = list(self.pf2.get_iter(P2))
        self.assertEquals(len(l), 1)
        self.assertEquals(l[0],(1,5))

    def test_iterate_over_their_capture_before_our_two(self):
        self.arc(P1, 2, ((2,4),(4,6),(5,7)))
        self.pf2.add_or_remove_take(P2, (1,5))
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 4)
        self.assertEquals(l[0],(1,5))
        twos = (2,4),(4,6),(5,7)
        self.assertIn(l[1], twos)
        self.assertIn(l[2], twos)
        self.assertIn(l[3], twos)

    def test_iterate_over_their_three_before_our_threat(self):
        self.arc(P1, 3, ((2,4),(4,6),))
        self.pf2.add_or_remove_threat(P2, (1,5))
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 3)
        threes = (2,4),(4,6)
        self.assertIn(l[0], threes)
        self.assertIn(l[1], threes)
        self.assertEquals(l[2],(1,5))
        
    def test_add_and_remove_length_candidate(self):
        self.arc(P1, 3, ((2,4),(4,6),), inc=1)
        self.pf2.add_or_remove_threat(P1, (1,5))
        self.arc(P1, 3, ((2,4),(4,6),), inc=-1)
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 1)
        self.assertEquals(l[0],(1,5))

    def test_add_and_remove_capture_candidate(self):
        self.pf2.add_or_remove_take(P1, (1,5), inc=1)
        self.pf2.add_or_remove_take(P1, (1,5), inc=-1)
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 0)

    def test_add_and_remove_threat_candidate(self):
        self.pf2.add_or_remove_threat(P1, (1,5), inc=1)
        self.pf2.add_or_remove_threat(P1, (1,5), inc=-1)
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 0)

    def test_add_and_remove_length_candidate_from_diff_directions(self):
        self.arc(P1, 3, ((2,4),(4,6),), inc=1)
        self.arc(P1, 3, ((2,4),(3,3),), inc=1)
        self.arc(P1, 3, ((2,4),(4,6),), inc=-1)
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 2)
        pair = ((2,4),(3,3),)
        self.assertIn(l[0], pair)
        self.assertIn(l[1], pair)

    def test_multiple_entries_searched_first(self):
        self.arc(P1, 3, ((2,4),(4,6),), inc=1)
        self.arc(P1, 3, ((2,4),(3,3),), inc=1)
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 3)
        self.assertEquals(l[0],(2,4))
        others = ((4,6), (3,3))
        self.assertIn(l[1], others)
        self.assertIn(l[2], others)

    def test_copy_is_deep(self):
        self.arc(P1, 3, ((2,4),(3,3),), inc=1)
        self.arc(P1, 4, ((3,3),), inc=1)
        bsc = self.pf2.copy()
        bsc.add_or_remove_candidates(P1, 4, [(3,3)], inc=-1)
        # Modifying the descendant should not have affected the parent
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(l[0],(3,3))


    def test_lost_positions_ignored_gracefully(self):
        self.arc(P1, 4, ((4,6),), inc=1)
        self.arc(P1, 4, ((5,7),), inc=1)
        self.arc(P1, 4, ((4,6),), inc=-1)
        l = list(self.pf2.get_iter(P1))
        self.assertEquals(len(l), 1)
        self.assertEquals(l[0],(5,7))

    def atest_one_opponent_double_three_must_be_block_cap_or_threatened(self):
        # i.e. a single instance of a double 3 attack must be blocked,
        # captured, or threatened, or we must extend a 3 of our own
        self.pf2.add_or_remove_take(P2, (1,5), inc=1)

        # Only their threes needs to be looked at, since there is a double 3
        self.arc(P1, 3, ((4,6),(5,6),), inc=1)
        self.arc(P1, 3, ((5,6),(9,6),), inc=1)

        # all our 3s should be included
        self.arc(P2, 3, ((4,8),(10,6),), inc=1)

        # only threats that threaten the double 3 really need considering (TODO)
        self.pf2.add_or_remove_threat(P2, (2,9), inc=1)

        # All 2s are irrelevant since there is a double 3
        self.arc(P2, 2, ((7,8),(8,8),(10,8)), inc=1)
        self.arc(P2, 2, ((8,8),(10,8),(12,8)), inc=1)
        self.arc(P2, 2, ((10,8),(12,8),(13,8)), inc=1)

        #st()
        l = list(self.pf2.get_iter(P2))

        self.assertEquals(len(l), 5)
        self.assertEquals(l[0], (5,6)) # Their open 3
        self.assertEquals(l[1], (1,5)) # Our take
        our_threes = ((4,8), (10,6)) # Our 3s
        self.assertIn(l[2], our_threes)
        self.assertIn(l[3], our_threes)
        self.assertEquals(l[4], (2,9)) # Our threat (TODO)

    def atest_three_plus_opponent_double_threes_cannot_block(self):
        # i.e. a single instance of a double 3 attack must be blocked,
        # captured, or threatened, or we must extend a 3 of our own
        self.pf2.add_or_remove_take(P2, (1,5), inc=1)

        # 3 x Two double attacks - can't block
        self.arc(P1, 3, ((4,6),(5,6),), inc=1)
        self.arc(P1, 3, ((5,6),(9,6),), inc=1)
        self.arc(P1, 3, ((4,6),(9,6),), inc=1)

        # all our 3s should be included
        self.arc(P2, 3, ((4,8),(10,6),), inc=1)

        # only threats that threaten the double 3 really need considering (TODO)
        self.pf2.add_or_remove_threat(P2, (2,9), inc=1)

        # All 2s are irrelevant since there is a double 3
        self.arc(P2, 2, ((7,8),(8,8),(10,8)), inc=1)
        self.arc(P2, 2, ((8,8),(10,8),(12,8)), inc=1)
        self.arc(P2, 2, ((10,8),(12,8),(13,8)), inc=1)

        l = list(self.pf2.get_iter(P2))
        self.assertEquals(len(l), 4)
        self.assertEquals(l[0], (1,5)) # Our take
        our_threes = ((4,8), (10,6)) # Our 3s
        self.assertIn(l[1], our_threes)
        self.assertIn(l[2], our_threes)
        self.assertEquals(l[3], (2,9)) # Our threat (TODO)

if __name__ == "__main__":
    unittest.main()

