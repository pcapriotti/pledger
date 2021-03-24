# Copyright (C) 2011 by Paolo Capriotti <p.capriotti@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import unittest
from pledger.sorting import Sorting, MapSorting, ExpressionSorting
from pledger.parser import Parser
from datetime import date


class TestSorting(unittest.TestCase):
    def setUp(self):
        self.data = [3, 5, 1, 2, 7, 4, 9, 6, 0, 8]
        self.parser = Parser()

    def testIdentitySorting(self):
        identity = Sorting(lambda x: x)
        self.assertEqual(self.data, identity(self.data))

    def testSimpleSorting(self):
        s = Sorting(lambda x: sorted(x))
        self.assertEqual(list(range(10)), s(self.data))

    def testInvertedSorting(self):
        s = ~Sorting(lambda x: sorted(x))
        self.assertEqual(list(reversed(range(10))), s(self.data))

    def testMapSorting(self):
        s = MapSorting(lambda x: x * (x - 4))
        self.assertEqual([2, 3, 1, 4, 0, 5, 6, 7, 8, 9], s(self.data))

    def testExpressionSorting(self):
        s = ExpressionSorting(self.parser, "record * (record - 4)")
        self.assertEqual([2, 3, 1, 4, 0, 5, 6, 7, 8, 9], s(self.data))

    def testExpressionSortingWithDate(self):
        s = ExpressionSorting(self.parser, "abs((record - date('2011/01/01')).days)")
        data = [date(2011, 2, 1), date(2010, 12, 15), date(2011, 9, 5), date(2010, 10, 2)]
        self.assertEqual(
            [date(2010, 12, 15), date(2011, 2, 1), date(2010, 10, 2), date(2011, 9, 5)],
            s(data))
