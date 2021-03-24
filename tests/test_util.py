import unittest
from pledger import util

class UtilTest(unittest.TestCase):
    def testItersplit(self):
        items = list(range(20))
        result =  [list(range(5)), list(range(6, 10)),
                   list(range(11, 15)), list(range(16, 20))]
        p = lambda x: x % 5 == 0
        self.assertEqual(result, list(util.itersplit(p, items)))

    def testObservable(self):
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

        self.assertEqual([1], invocations)

    def testLinearized(self):
        self.assertEqual([1,2,3], util.linearized([(1, []),(2, []),(3, [])]))
        self.assertEqual([1,2,3,4,5,6],
            util.linearized([
                (1, [(2, []), (3, [(4, [])])]),
                (5, []),
                (6, [])]))

class PrefixTreeTest(unittest.TestCase):
    def setUp(self):
        self.tree = util.PrefixTree()

    def testEmpty(self):
        self.assertEqual([], self.tree.from_prefix(""))

    def testUnambiguous(self):
        self.tree.insert("hello")
        self.tree.insert("world")
        self.assertItemsEqual(["hello"], self.tree.from_prefix("h"))

    def testAmbiguous(self):
        self.tree.insert("hello")
        self.tree.insert("help")
        self.tree.insert("haste")
        self.assertItemsEqual(["hello", "help"],
                              self.tree.from_prefix("he"))

    def testConstruction(self):
        words = ["hello", "world"]
        tree = util.PrefixTree(words)
        self.assertItemsEqual(words, tree.from_prefix(""))

    def testFail(self):
        self.tree.insert("hello")
        self.assertItemsEqual([], self.tree.from_prefix("g"))
        self.assertItemsEqual([], self.tree.from_prefix("help"))
