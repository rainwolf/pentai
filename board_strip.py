from defines import *

class BoardStrip():
    def __init__(self, initial_val=0):
        self.occs = initial_val

    def clone(self):
        bs = BoardStrip(self.occs)
        return bs
        
    def get_occ(self, ind):
        ret = self.occs >> (2 * ind)
        return ret & 3

    def set_occ(self, ind, occ):
        shift = 4 ** ind
        self.occs &= ~(shift + shift * 2)
        self.occs |= (occ * shift)

    def get_occ_list(self, min_ind, max_ind):
        ol = [self.get_occ(i) for i in range(min_ind, 1+max_ind)]
        return ol

    def match_five_in_a_row(self, move_ind, my_colour):
        l = 1
        while l < 5:
            test_ind = move_ind + l
            next_occ = self.get_occ(test_ind)
            if next_occ != my_colour:
                break
            l += 1

        # Now see how far the line goes in the opposite direction.
        m = -1
        while m > -5:
            test_ind = move_ind + m
            if test_ind < 0:
                # Other end of a potential line is off the edge of the board
                break
            next_occ = self.get_occ(test_ind)
            if next_occ != my_colour:
                break
            m -= 1
        total_line_length = 1 + (l-1) - (m+1)
        return total_line_length >= 5

    def match_capture_left(self, ind, colour):
        if colour == BLACK:
            return self.match_black_capture_left(ind)
        else:
            return self.match_white_capture_left(ind)

    def match_black_capture_left(self, ind):
        # BWWx
        if ind < 3:
            # Cannot capture to the left - off the board
            return ()
        shift = 4 ** (ind - 3)
        occs = (self.occs / shift) & (4 ** 4 - 1)
        pattern = BLACK + (4 * WHITE) + (16 * WHITE) # + 64 * 0
        if occs == pattern:
            return (ind-1, ind-2)
        return ()

    def match_white_capture_left(self, ind):
        # WBBx
        if ind < 3:
            # Cannot capture to the left - off the board
            return ()
        shift = 4 ** (ind - 3)
        occs = (self.occs / shift) & (4 ** 4 - 1)
        pattern = WHITE + (4 * BLACK) + (16 * BLACK) # + 64 * 0
        if occs == pattern:
            return (ind-1, ind-2)
        return ()

    def match_capture_right(self, ind, colour):
        if colour == BLACK:
            return self.match_black_capture_right(ind)
        else:
            return self.match_white_capture_right(ind)

    def match_black_capture_right(self, ind):
        # xWWB
        shift = 4 ** ind
        occs = (self.occs / shift) & (4 ** 4 - 1)
        pattern = (WHITE + (4 * WHITE) + (16 * BLACK)) * 4
        if occs == pattern:
            return (ind+1, ind+2)
        return ()

    def match_white_capture_right(self, ind):
        # xBBW
        shift = 4 ** ind
        occs = (self.occs / shift) & (4 ** 4 - 1)
        pattern = (BLACK + (4 * BLACK) + (16 * WHITE)) * 4
        if occs == pattern:
            return (ind+1, ind+2)
        return ()

    def get_capture_indices(self, ind, colour):
        captures = []
        if colour == BLACK:
            captures.extend(self.match_black_capture_left(ind))
            captures.extend(self.match_black_capture_right(ind))
        else:
            # WHITE
            captures.extend(self.match_white_capture_left(ind))
            captures.extend(self.match_white_capture_right(ind))
        return captures

