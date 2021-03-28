from pledger.sorting import Sorting, MapSorting, ExpressionSorting
from pledger.parser import Parser
from datetime import date
import pytest


@pytest.fixture
def data():
    return [3, 5, 1, 2, 7, 4, 9, 6, 0, 8]


def test_identity_sorting(data):
    identity = Sorting(lambda x: x)
    assert data == identity(data)


def test_simple_sorting(data):
    s = Sorting(lambda x: sorted(x))
    assert s(data) == list(range(10))


def test_inverted_sorting(data):
    s = ~Sorting(lambda x: sorted(x))
    assert s(data) == list(reversed(range(10)))


def test_map_sorting(data):
    s = MapSorting(lambda x: x * (x - 4))
    assert s(data) == [2, 3, 1, 4, 0, 5, 6, 7, 8, 9]


def test_expression_sorting(parser, data):
    s = ExpressionSorting(parser, "record * (record - 4)")
    assert s(data) == [2, 3, 1, 4, 0, 5, 6, 7, 8, 9]


def test_expression_sorting_with_date(parser):
    s = ExpressionSorting(parser, "abs((record - date('2011/01/01')).days)")
    data = [date(2011, 2, 1), date(2010, 12, 15),
            date(2011, 9, 5), date(2010, 10, 2)]
    assert s(data) == [date(2010, 12, 15), date(2011, 2, 1),
                       date(2010, 10, 2), date(2011, 9, 5)]
