#!/usr/bin/env python

import unittest

from priority_filter import *
from blindness_filter import *

class BlindnessFilterTest(unittest.TestCase):
    def setUp(self):
        random.seed(1)
        self.priority_filter = PriorityFilter()
        self.bf = BlindnessFilter(self.priority_filter)

    def arc(self, *args, **kwargs):
        self.bf.add_or_remove_candidates(*args, **kwargs)

    def test_default_no_blindness(self):
        self.arc(BLACK, 4, ((4,6),), inc=1)
        l = list(self.bf.get_iter(BLACK))
        self.assertEquals(len(l), 1)
        self.assertEquals(l[0],(4,6))

    def test_set_total_blindness_lets_one_through(self):
        for i in range(10):
            self.arc(BLACK, 4, ((i,i),), inc=1)
        self.bf.set_blindness(1)
        l = list(self.bf.get_iter(BLACK))
        self.assertEquals(len(l), 1)

    def test_set_partial_blindness_lets_some_through(self):
        for i in range(10):
            self.arc(BLACK, 4, ((i,i),), inc=1)
        self.bf.set_blindness(0.5)
        l = list(self.bf.get_iter(BLACK))
        self.assertGreater(len(l), 2)
        self.assertLess(len(l), 8)

    def test_copy(self):
        self.bf.set_blindness(.9999)
        self.arc(BLACK, 4, ((4,6),), inc=1)
        self.bf = self.bf.copy()
        self.assertEquals(self.bf.blindness, .9999)
        l = list(self.bf.get_iter(BLACK))
        self.assertEquals(len(l), 1)

if __name__ == "__main__":
    unittest.main()
