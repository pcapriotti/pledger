from pledger import util
import pytest


def test_itersplit():
    items = list(range(20))
    result = [
        list(range(5)),
        list(range(6, 10)),
        list(range(11, 15)),
        list(range(16, 20)),
    ]

    def p(x):
        return x % 5 == 0

    assert list(util.itersplit(p, items)) == result


def test_observable():
    invocations = []

    class Obs(util.Observable):
        def foo(self):
            self.fire("foo", 1)

    class Listener(object):
        def on_foo(inner, arg):
            invocations.append(arg)

    obs = Obs()
    listener = Listener()
    obs.add_listener(listener)
    obs.add_listener(object())

    obs.foo()

    assert invocations == [1]


def test_linearized():
    assert util.linearized([(1, []), (2, []), (3, [])]) == [1, 2, 3]
    assert util.linearized([(1, [(2, []), (3, [(4, [])])]), (5, []), (6, [])]) == [
        1,
        2,
        3,
        4,
        5,
        6,
    ]


@pytest.fixture
def tree():
    return util.PrefixTree()


def test_empty(tree):
    assert tree.from_prefix("") == []


def test_unambiguous(tree):
    tree.insert("hello")
    tree.insert("world")
    assert tree.from_prefix("h") == ["hello"]


def test_ambiguous(tree):
    tree.insert("hello")
    tree.insert("help")
    tree.insert("haste")
    assert tree.from_prefix("he") == ["hello", "help"]


def test_construction():
    words = ["hello", "world"]
    tree = util.PrefixTree(words)
    assert set(tree.from_prefix("")) == set(words)


def test_fail(tree):
    tree.insert("hello")
    assert tree.from_prefix("g") == []
    assert tree.from_prefix("help") == []
