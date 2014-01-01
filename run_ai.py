#!/usr/bin/env python

import gui
import human_player
import rules
import game

import time

from ai_player import *
from priority_filter import *
from budget_searcher import *

import pdb

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
        self.mmpdl = 12
        self.narrowing = 1

        self.capture_score_base = 1000
        self.take_score_base = 600
        self.threat_score_base = 60
        self.captures_scale = [0, 1, 1, 1, 1, 1]
        self.length_factor = 29
        self.move_factor = 300
        self.sub = False

    def create_player(self, name, budget=0):
        if budget > 0:
            sf = BudgetSearcher(budget)
        else:
            sf = PriorityFilter()
            sf.set_max_moves_per_depth_level(mmpdl=9, narrowing=0)
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

        player.set_max_depth(self.max_depth)
        # TODO: pf = player.get_priority_filter()

class MatchResults():
    def __init__(self):
        self.results = []
        self.bw_total = [0, 0, 0]
        self.dc_total = {"Defender":0, "Contender":0}

    def __repr__(self):
        return "\n".join(self.results) + "\nB/W:" + str(self.bw_total) + " D/C: " + str(self.dc_total)

    def add(self, result):
        res_str, winner_colour, winner_name = result
        self.results.append(res_str)
        self.bw_total[winner_colour] += 1
        self.dc_total[str(winner_name)] += 1

class Match():
    def __init__(self):
        self.genome1 = Genome()
        self.genome2 = Genome()

    def set_up(self):
        self.p1 = self.genome1.create_player("Defender")
        self.p2 = self.genome2.create_player("Contender", 9)

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

        print "Game was won by: %s" % winner_name
        print tt

        return "%s vs. %s: %s (%sx%s %s) %s" % (p1.name, p2.name, winner_name,
                board_size, board_size, p1.max_depth, tt), winner, winner_name

    def play_some_games(self):
        #pdb.set_trace()
        #self.genome2.move_factor = 350
        #self.genome2.length_factor = 29
        #self.genome2.take_score_base = 550
        #self.genome2.capture_score_base = 600
        #self.genome2.threat_score_base = 60
        #self.genome2.narrowing = 2
        #self.genome2.max_depth += 2 # Setting max_depth here doesn't work
        #self.genome1.max_depth += 1
        #self.genome2.mmpdl = 16
        #self.genome2.captures_scale = [0, 1, 1, 2, 3, 4]
        #self.genome2.move_factor = 10000000

        results = MatchResults()
        for game_length in range(1, 5):
            for board_size in [9, 13, 19]:
                for first_player in [0, 1]:
                    self.set_up()
                    self.p1.set_max_depth(game_length)
                    self.p2.set_max_depth(game_length)
                    players = [self.p1, self.p2]
                    second_player = 1 - first_player
                    res = self.play_one_game(board_size,
                                             players[first_player],
                                             players[second_player])
                    results.add(res)

        print results


if __name__ == "__main__":
    m = Match()
    m.play_some_games()
