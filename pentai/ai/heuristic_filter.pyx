from pentai.base.defines import *

import random

def max_moves_sample_func(depth):
    return 9

class HeuristicFilter(object):
    def __init__(self, orig=None, min_priority=0):

        self.max_moves_func = max_moves_sample_func
        if orig != None:
            self.max_moves_func = orig.max_moves_func
        self.vision = 100

        self.heuristic = None
        self.reset(orig, min_priority)

    def set_vision(self, val):
        self.vision = val

    def set_heuristic(self, heuristic):
        self.heuristic = heuristic

    def set_max_moves_per_depth_level(self, mmpdl, narrowing, chokes=[]):
        if narrowing != 0:
            def mmpdl_func(depth):
                # This is really hacky, but it seemed to work
                for d, w in chokes:
                    if depth >= d:
                        return w
                return mmpdl - round(narrowing * depth)
        else:
            def mmpdl_func(depth):
                # This is really hacky, but it seemed to work
                for d, w in chokes:
                    if depth >= d:
                        return w
                return mmpdl

        self.set_max_moves_func(mmpdl_func)

    def reset(self, orig=None, min_priority=0):
        if orig != None:
            ocbpc = orig.candidates_by_priority_and_colour
            self.heuristic = orig.heuristic
        self.candidates_by_priority_and_colour = []
        cbpc = self.candidates_by_priority_and_colour

        for priority in range(6):
            l = []
            cbpc.append(l)
            for colour in range(3):
                if priority < min_priority or orig is None:
                    l.append({})
                else:
                    l.append(ocbpc[priority][colour].copy())
        if self.heuristic:
            self.heuristic.reset()

    def set_max_moves_func(self, mmf):
        self.max_moves_func = mmf

    def copy(self, min_priority=0):
        return HeuristicFilter(orig=self, min_priority=min_priority)

    def get_iter(self, our_colour, depth=0, min_priority=0, tried=None):
        if tried is None:
            tried = set()
        candidates = []

        other_colour = opposite_colour(our_colour)

        cbpc = self.candidates_by_priority_and_colour
        for length in range(1 + 5 - min_priority): # TODO constants
            priority = 5 - length
            cand_for_priority = cbpc[priority]
            for colour in (our_colour, other_colour):
                slot = cand_for_priority[colour]
                slot_arr = slot.iteritems()
                #sorted_slot = [(count, pos) for (pos, count) in slot_arr]
                #sorted_slot.sort(reverse=True)
                #for count, pos in sorted_slot:
                for pos, count in slot_arr:
                    if count > 0:
                        if not pos in tried:
                            if self.vision < 100:
                                if random.random() * 100 > self.vision:
                                    # Can't see that sorry ;)
                                    continue
                            tried.add(pos)
                            #yield pos
                            candidates.append(pos)
                            if len(tried) >= self.max_moves_func(depth):
                                # return
                                break

            hw = self.heuristic.get_weighting
            sorted_candidates = [(hw(m, depth), m) for m in candidates]
            sorted_candidates.sort(reverse=True)

            for w, c in sorted_candidates:
                yield c

    def __repr__(self):
        return "%s" % self.candidates_by_priority_and_colour[5]

    def add_or_remove_candidates(self, colour, length, pos_list, inc=1):
        if length == 5:
            # won already, ignore
            return
        if length == 4: # allow space for capture priority
            length = 5
        if length < 3:  # allow space for threat priority
            length -= 1
        slot = self.candidates_by_priority_and_colour[length][colour]
        for pos in pos_list:
            assert pos[0] >= 0
            assert pos[1] >= 0
            slot[pos] = slot.setdefault(pos, 0) + inc
            # Remove - still a value of 0 here, which is ignored in get_iter()

    def add_or_remove_take(self, colour, pos, inc=1):
        assert pos[0] >= 0
        assert pos[1] >= 0
        # Valuing captures between 3s and 4s
        slot = self.candidates_by_priority_and_colour[4][colour]
        slot[pos] = slot.setdefault(pos, 0) + inc

    def add_or_remove_threat(self, colour, pos, inc=1):
        assert pos[0] >= 0
        assert pos[1] >= 0
        # Valuing captures between 2s and 3s
        slot = self.candidates_by_priority_and_colour[2][colour]
        slot[pos] = slot.setdefault(pos, 0) + inc
