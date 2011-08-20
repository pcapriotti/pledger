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
