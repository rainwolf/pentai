# TODO: This will need to be increased to 6 for pente-keryo
cdef int COUNT_LENGTH
COUNT_LENGTH=5

from pentai.base.defines import *

cimport cython

from libc.stdint cimport uint64_t as U64
"""
Detect and report indices that build on or interfere with a 
possibly fragmented line, as well as counting these possibilities.
Here, we build a lookup table, which is a mapping from a bit pattern
to the information we need - the colour, current length and empty indices
of the row of 5 positions that we are currently looking at.
"""
cdef U64 FIVE_OCCS_MASK
FIVE_OCCS_MASK = (4 ** 5 - 1)

global length_lookup
length_lookup = {}

candidate_lookup = [3,1,0,2,4]

def extend_and_store_lookups(occ, depth, occ_val, length, colour, empty_list, rep_str):
    """
    occ is the colour of the stone (or EMPTY) that we are extending by
    depth is the length yet to be added
    occ_val is the total value so far, representing the stretch to the left
    that we have already processed.
    length is the number of stones seen so far in that stretch. They will all
    have been of the same 'colour' as we only care about and store them if
    they are.
    rep_str is a representation of the stones seen so far, for debugging.
    """
    if occ != EMPTY:
        # add occ to lookup value
        occ_val += colour

        # add one to length
        length += 1
        rep_str = rep_str + str(colour)
    else:
        rep_str = rep_str + " "
        empty_list.append(depth)

    if depth <= 0:
        if length > 0:
            # add_pattern
            assert length <= 5
            rep_str = rep_str + ">"
            sub_type = calc_subtype_from_empty_list(empty_list)
            candidates = [(candidate_lookup[i], i) for i in empty_list]
            candidates.sort()
            candidates = [i for o,i in candidates]
            length_lookup[occ_val] = colour, length, sub_type, candidates, rep_str
    else:
        # Recursively add to the stretch
        build_and_store_values(depth-1, occ_val, length, colour, empty_list[:], rep_str)

def calc_subtype_from_empty_list(empty_list):
    el = sorted(empty_list)
    lel = len(empty_list)
    if lel == 0:
        # all 5
        return 0
    elif lel == 1:
        # 4 / 5
        if el[0] == 2:
            # gap in middle
            return 0
        elif el[0] in (1,3):
            # gap to the side
            return 1
        else:
            # gap at end
            return 2
    elif lel == 2:
        # 3 / 5
        if el in ([0,1], [0,4], [3,4]):
            # solid
            return 2
        elif el == ([1,3]):
            # evenly spread X.X.X
            return 1
        else:
            # gap in middle .X.XX, X..XX etc.
            return 0
    elif lel == 3:
        # 2 / 5
        if el in ([1,3,4], [0,2,4], [0,1,3]):
            # single gap between pieces - ideal
            return 2
        elif el == [1,2,3]:
            # gap to the side
            return 1
        else:
            # Not so good
            return 0
    # else lel == 4, no structure to report
    return 0

def build_and_store_values(depth, occ_val, length, colour, empty_list, rep_str=None):
    """ Add one stone or empty place """
    # For debugging.
    if rep_str == None:
        rep_str = "<"

    # Shift what we've seen so far to the right
    occ_val *= 4
    for occ in (EMPTY, colour):
        extend_and_store_lookups(occ, depth, occ_val, length, colour, empty_list[:], rep_str)


def prepare_length_lookups():
    """ Build the entire lookup table """
    # We only care about stretches of 5 with one colour and empties in it.
    build_and_store_values(4, 0, 0, P1, [])
    build_and_store_values(4, 0, 0, P2, [])

# TODO: Something better than a global
prepare_length_lookups()

#@cython.profile(False)
cpdef process_substrips(U64 bs, int min_ind, int max_ind, us, int inc):
    """
    Try to match each stretch of 5 positions against our lookup table.
    If we find a match then report the number of stones of the same
    colour via length_counters, and report the empty locations (indices)
    for use by the search filter (us = UtilityStats)
    If we are removing the contributions, inc will be set to -1
    """
    cdef int ind
    cdef int shift
    cdef U64 occs
    cdef int colour
    cdef int length

    for ind in range(min_ind, max_ind+1-4):
        # Extract just the 5 * 2 bits that we're currently interested in.
        shift = ind << 1 # x 2 for 2 bits each occ - EMPTY:0, P1:1 or P2:2
        occs = (bs >> shift) & FIVE_OCCS_MASK

        # Now see if it's in our lookup table
        try:
            colour, length, sub_type, empty_list, rep_str = length_lookup[occs]
        except KeyError:
            # Nope. Not interesting.
            continue

        # Report it
        shifted_empties = [e+ind for e in empty_list]
        us.report_length_candidate(colour, length, sub_type, shifted_empties, inc)

