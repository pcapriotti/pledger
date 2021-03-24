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
