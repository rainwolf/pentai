cimport pentai.base.board_strip as bs_m
import pentai.ai.length_lookup_table as llt_m
from pentai.base.defines import *
# cython: profile=True

from libc.stdint cimport uint64_t as U64
# U64 = int # For debugging as .py

cimport cython

# TODO: move this to test code?
def pass_through_func(a, ignored):
    """ This is just a stub, shouldn't be called in production code. """
    return (a, 0)

class UtilityStats(object):

    def __init__(self, parent=None, search_filter=None):
        if parent == None:
            self.search_filter = search_filter
            self.i_to_p = pass_through_func
            self.checkerboard_stats = [None, [0,0],[0,0]]
            self.reset()

            # TODO: move this to test code?
            self.s_num = 0 # irrel, just needs a value
        else:
            # Manual deep copy
            pl = parent.lines
            self.lines = [None, pl[P1][:], pl[P2][:]]
            pcs = parent.checkerboard_stats
            self.checkerboard_stats = [None, pcs[P1][:], pcs[P2][:]]
            self.takes = parent.takes[:]
            self.threats = parent.threats[:]
            self.enclosed_four = parent.enclosed_four[:]
            # TODO: Use depth and/or min priority when copying the search filter
            self.search_filter = parent.search_filter.copy()
            self.s_num = 0 # irrel, just needs a value

    def reset(self):
        self.lines = [None, [0] * 5, [0] * 5]
        self.takes = [0, 0, 0]
        self.threats = [0, 0, 0]
        self.enclosed_four = [0, 0, 0]
        if self.search_filter != None:
            self.search_filter.reset()

    def __repr__(self):
        return "Lines: %s, Takes: %s, Threats: %s, Best: %s" % \
                (self.lines, self.takes, self.threats, self.search_filter)

    def before_set_occ(self, game, pos, colour, board, rules):
        set_or_reset_occs(self, board, rules, pos, -1)
        self.update_checkerboard_stats(colour, pos, -1)

    def after_set_occ(self, game, pos, colour, board, rules):
        set_or_reset_occs(self, board, rules, pos, 1)
        self.update_checkerboard_stats(colour, pos, 1)

    def report_length_candidate(self, colour, length, ind_list, inc):
        report_length_candidate(self, colour, length, ind_list, inc)

    def report_take(self, colour, ind, inc):
        self.takes[colour] += inc
        pos = self.i_to_p(ind, self.s_num)
        self.search_filter.add_or_remove_take(colour, pos, inc)
        
    def report_threat(self, colour, ind, inc):
        self.threats[colour] += inc
        pos = self.i_to_p(ind, self.s_num)
        self.search_filter.add_or_remove_threat(colour, pos, inc)

    def report_enclosed_four(self, colour, inc):
        self.enclosed_four[colour] += inc

    def set_ind_to_pos(self, func, s_num):
        # These two should always be set together
        self.i_to_p = func
        self.s_num = s_num
    
    #@cython.profile(False)
    def update_checkerboard_stats(self, colour, pos, int inc):
        if not colour:
            # We don't care about empty spaces
            return

        x, y = pos
        square_colour = (x % 2) ^ (y % 2)

        cb_stats_for_colour = self.checkerboard_stats[colour]
        cb_stats_for_colour[square_colour] += inc

# This is called LOTS of times
#@cython.profile(False)
cdef report_length_candidate(self, int colour, int length, ind_list, int inc):
    self.lines[colour][length-1] += inc

    # TODO: Can this be done even faster?
    i_to_p = self.i_to_p
    s_num = self.s_num
    pos_list = [i_to_p(i, s_num) for i in ind_list]

    self.search_filter.add_or_remove_candidates(
            colour, length, pos_list, inc)

#@cython.profile(False)
cdef inline set_or_reset_occs(self, brd, rules, pos, int inc):
    cdef U64 bs
    cdef int ind, s_num, strip_min, strip_max, brd_size, ccp
    cdef int min_ind, max_ind

    # update substrips
    ccp = rules.can_capture_pairs
    brd_size = brd.get_size()

    for ds in brd.get_direction_strips():
        # Keep track of the lengths of lines that can form 5
        # in a row

        bs, s_num = ds.get_strip(pos)
        ind = ds.get_index(pos)

        strip_min, strip_max = ds.get_bounds(s_num, brd_size)

        self.set_ind_to_pos(ds.get_pos, s_num)

        # These are the absolute indices that bound the strip
        # that we want to use to adjust length stats.
        min_ind = max(strip_min, ind-4) # TODO: constants
        max_ind = min(ind+4, strip_max) # inclusive

        # These have different parameter lists because of the different
        # lengths of the matching required.
        # TODO move min_ind into process_substrips
        llt_m.process_substrips(bs, min_ind, max_ind, self, inc)

        if ccp:
            # TODO: Put these in one function
            bs_m.process_takes(bs, ind, strip_min, strip_max, self, inc)
            bs_m.process_threats(bs, ind, strip_min, strip_max, self, inc)

        bs_m.process_enclosed_fours(bs, ind, self, inc)

