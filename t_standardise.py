#!/usr/bin/env python

import unittest

from game_state import *
from game import *
from openings_db import *
from rules import *
from standardise import *

import pdb

class StandardiseTest(unittest.TestCase):
    def setUp(self):
        self.rules = Rules(9, "standard")
        self.game = Game(self.rules, Player("BC"), Player("Whoever"))

    def test_page_flip(self): # TODO: rename to flip
        self.game.load_moves("1. (0,0)\n2. (3,3)\n3. (3,4)\n4. (5,4)")
        gpf = page_flip(self.game.current_state)
        brd = gpf.get_board()

        self.assertEqual(brd.get_occ((8,0)), BLACK)
        self.assertEqual(brd.get_occ((5,3)), WHITE)
        self.assertEqual(brd.get_occ((5,4)), BLACK)
        self.assertEqual(brd.get_occ((3,4)), WHITE)

    def test_calendar_flip(self):
        self.game.load_moves("1. (0,0)\n2. (3,3)\n3. (3,4)\n4. (5,4)")
        gcf = calendar_flip(self.game.current_state)
        brd = gcf.get_board()

        self.assertEqual(brd.get_occ((0,8)), BLACK)
        self.assertEqual(brd.get_occ((3,5)), WHITE)
        self.assertEqual(brd.get_occ((3,4)), BLACK)
        self.assertEqual(brd.get_occ((5,4)), WHITE)

    def test_diagonal_flip(self):
        """ i.e. swap x and y """
        self.game.load_moves("1. (0,0)\n2. (3,3)\n3. (3,4)\n4. (5,4)")
        gdf = diagonal_flip(self.game.current_state)
        brd = gdf.get_board()

        self.assertEqual(brd.get_occ((0,0)), BLACK)
        self.assertEqual(brd.get_occ((3,3)), WHITE)
        self.assertEqual(brd.get_occ((4,3)), BLACK)
        self.assertEqual(brd.get_occ((4,5)), WHITE)

    def test_diagonal_flip(self):
        """ i.e. swap x and y """
        self.game.load_moves("1. (0,0)\n2. (3,3)\n3. (3,4)\n4. (5,4)")
        gdf = diagonal_flip(self.game.current_state)
        brd = gdf.get_board()

        self.assertEqual(brd.get_occ((0,0)), BLACK)
        self.assertEqual(brd.get_occ((3,3)), WHITE)
        self.assertEqual(brd.get_occ((4,3)), BLACK)
        self.assertEqual(brd.get_occ((4,5)), WHITE)

    def test_diagonal_then_page(self):
        self.game.load_moves("1. (0,0)\n2. (3,3)\n3. (3,4)\n4. (5,4)")
        gdf = diagonal_flip(self.game.current_state)
        gpf = page_flip(self.game.current_state)
        brd = gpf.get_board()

        self.assertEqual(brd.get_occ((8,0)), BLACK)
        self.assertEqual(brd.get_occ((5,3)), WHITE)
        self.assertEqual(brd.get_occ((4,3)), BLACK)
        self.assertEqual(brd.get_occ((4,5)), WHITE)

    def test_diagonal_then_calendar(self):
        #pdb.set_trace()
        self.game.load_moves("1. (0,0)\n2. (3,3)\n3. (3,4)\n4. (5,4)")
        gdf = diagonal_flip(self.game.current_state)
        gcf = calendar_flip(self.game.current_state)
        brd = gcf.get_board()
        #print brd

        self.assertEqual(brd.get_occ((0,8)), BLACK)
        self.assertEqual(brd.get_occ((3,5)), WHITE)
        self.assertEqual(brd.get_occ((4,5)), BLACK)
        self.assertEqual(brd.get_occ((4,3)), WHITE)
'''
def standardise(state):
    copy state
    for operation in ops:
        if state in db
            return state
        apply operation to state
'''
