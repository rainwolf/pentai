#!/usr/bin/env python

import gui
import human_player
import rules
import game

import time

from ai_player import *
from priority_filter import *
from blindness_filter import *
from budget_searcher import *

import pdb


import pstats, cProfile


class TwoTimer:
    def __init__(self):
        self.totals = [0.0, 0.0]
        self.current = 0

    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.totals[self.current] += self.end - self.start
        self.current = 1 - self.current

    def __repr__(self):
        tot = self.totals
        return "B: %.2fs, W: %.2fs, B/W: %.2f" % (tot[0], tot[1], tot[0]/tot[1])

class Genome():
    """
    max_depth
    width (max_moves_per_depth_level)
    narrowing: 0, 1, .5, -0.5 (per depth level)
    line base
    capture_score_base
    take_score_base
    threat_score_base
    capture scaling
    line length scaling
    the value of the move
    max_time_per_move (proportion of remaining time)
    total game time
    search iterations - 0,1,2,3
    """
    def __init__(self):
        self.max_depth = 6
        self.mmpdl = 9
        self.narrowing = 0
        self.chokes = [(4,2)]

        self.capture_score_base = 300
        self.take_score_base = 100
        self.threat_score_base = 20
        self.captures_scale = [0, 1, 1, 1, 1, 1]
        self.length_factor = 27
        self.move_factor = 30
        self.blindness = 0
        self.sub = True

    def create_player(self, name, budget=0):
        #pdb.set_trace()
        if budget > 0:
            sf = BudgetSearcher(budget)
        else:
            sf = PriorityFilter()
            sf.set_max_moves_per_depth_level(mmpdl=self.mmpdl, narrowing=self.narrowing,
                    chokes=self.chokes)
        if self.blindness > 0:
            bf = BlindnessFilter(sf)
            bf.set_blindness(self.blindness)
            sf = bf
        p = AIPlayer(sf, name=name)
        self.set_config(p)

        return p

    def set_config(self, player):
        uc = player.get_utility_calculator()
        uc.capture_score_base = self.capture_score_base
        uc.take_score_base = self.take_score_base
        uc.threat_score_base = self.threat_score_base
        uc.captures_scale = self.captures_scale
        uc.length_factor = self.length_factor
        uc.move_factor = self.move_factor
        uc.sub = self.sub

        self.max_depth_boost = 0
        # TODO: pf = player.get_priority_filter()

class MatchResults():
    def __init__(self):
        self.results = []
        self.bw_total = [0, 0, 0]
        self.dc_total = {"Defender":0, "Contender":0}
        self.total_ratio = 0.
        self.games_played = 0

    def __repr__(self):
        return "\n".join(self.results) + "\nB/W:" + str(self.bw_total) \
                + " won: " + str(self.dc_total) \
                + " C/D avg. time: " + str(self.total_ratio / self.games_played)

    def add(self, result):
        res_str, winner_colour, winner_name, ratio = result
        self.results.append(res_str)
        self.bw_total[winner_colour] += 1
        self.dc_total[str(winner_name)] += 1
        self.total_ratio += ratio
        self.games_played += 1

class Match():
    def __init__(self):
        #pdb.set_trace()
        self.genome1 = Genome()
        self.genome2 = Genome()

    def set_up(self, game_length):
        self.p1 = self.genome1.create_player("Defender")
        self.p2 = self.genome2.create_player("Contender")
        self.p1.set_max_depth(game_length + self.genome1.max_depth_boost)
        self.p2.set_max_depth(game_length + self.genome2.max_depth_boost)

    def play_one_game(self, board_size, p1, p2):
        r = rules.Rules(board_size, "standard")
        self.game = game.Game(r, p1, p2)

        tt = TwoTimer()

        while not self.game.finished():
            p = self.game.get_current_player()
            with tt:
                m = p.do_the_search()
                self.game.make_move(m)
        #pdb.set_trace()
        winner_name = self.game.winner_name()
        winner = self.game.winner()
        if p1.name == "Contender":
            ratio = tt.totals[0] / tt.totals[1]
        else:
            ratio = tt.totals[1] / tt.totals[0]

        print "Game was won by: %s" % winner_name
        print tt
 
        return "%s vs. %s: %s (%sx%s %s) %s" % (p1.name, p2.name, winner_name,
                board_size, board_size, p1.max_depth, tt), winner, winner_name, ratio

    def play_some_games(self):

        #self.genome2.length_factor = 35
        #self.genome2.take_score_base = 110
        #self.genome2.capture_score_base = 310
        #self.genome2.threat_score_base = 25
        self.genome1.blindness = 0.30
        self.genome2.blindness = 0.40

        #self.genome2.narrowing = 3
        #self.genome2.max_depth += 2 # Setting max_depth here doesn't work
        #self.genome2.mmpdl = 15
        #self.genome2.chokes = []
        #self.genome2.chokes = [(4,3),(5,1)]
        #self.genome2.chokes = [(2,2)]
        #self.genome1.max_depth_boost = 2
        #self.genome2.captures_scale = [0, 1, 10, 100, 1000, 50]
        #self.genome2.captures_scale = [0, 0, 0, 0, 0, 0]
        #self.genome2.move_factor = 10000000

        self.genome1.sub = False
        self.genome2.sub = False
        #self.genome2.move_factor = 50
        #self.genome2.move_factor = 5

        results = MatchResults()
        for game_length in range(1, 3):
            #for board_size in [9, 13, 19]:
            for board_size in [9, 13, 16, 19]:
                for first_player in [0, 1]:
                    self.set_up(game_length)
                    players = [self.p1, self.p2]
                    second_player = 1 - first_player
                    res = self.play_one_game(board_size,
                                             players[first_player],
                                             players[second_player])
                    results.add(res)

        print results

import random

if __name__ == "__main__":
    random.seed()
    m = Match()
    '''
    m.play_some_games()
    '''
    cProfile.runctx("m.play_some_games()", globals(), locals(), "Profile.prof")

    s = pstats.Stats("Profile.prof")
    s.strip_dirs().sort_stats("time").print_stats()
