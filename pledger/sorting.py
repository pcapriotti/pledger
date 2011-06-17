class Sorting(object):
    def __init__(self, sorter):
        self.sorter = sorter

    def __invert__(self):
        @Sorting
        def result(l):
            return list(reversed(self(l)))
        return result

    def __call__(self, l):
        return self.sorter(l)

class MapSorting(Sorting):
    def __init__(self, map):
        self.map = map

    def __call__(self, list):
        l = [(self.map(x), x) for x in list]
        l.sort()
        return [x for (v, x) in l]

class ExpressionSorting(MapSorting):
    def __init__(self, parser, expression):
        self.parser = parser
        self.expression = compile(expression, "<commandline>", "eval")

    def map(self, entry):
        context = {
                "record": entry,
                "date": self.parse_date }
        return eval(self.expression, context)

    def parse_date(self, str):
        return self.parser.parse_fuzzy_date(str)
