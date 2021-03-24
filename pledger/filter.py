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

from pledger.flag import FlagMetaclass
from pledger.value import ZERO

class Filter(object, metaclass=FlagMetaclass):
    flags = []

    def __init__(self, predicate):
        self.predicate = predicate

    def __call__(self, *args):
        return self.predicate(*args)

    def __and__(self, other):
        @Filter
        def result(*args):
            return self(*args) and other(*args)
        return result

    def __or__(self, other):
        @Filter
        def result(*args):
            return self(*args) or other(*args)
        return result

    def __invert__(self):
        @Filter
        def result(*args):
            return not self(*args)
        return result

    @classmethod
    def has_account(cls, account):
        @cls
        def result(transaction, entry):
            return entry.account == account
        return result

    @classmethod
    def matches(cls, regexp):
        @cls
        def result(transaction, entry):
            return regexp.search(entry.account.name) is not None
        return result

    @classmethod
    def parse(cls, parser, *args):
        return cls(*args)

Filter.null = Filter(lambda transaction, entry: True)

class DateFilter(Filter):
    @classmethod
    def parse(cls, parser, str):
        date = parser.parse_fuzzy_date(str)
        if date:
            return cls(date)
        else:
            raise ValueError("Invalid date")

    def __init__(self, date):
        self.date = date

class BeginFilter(DateFilter):
    flag = "begin"
    args = 1

    def __call__(self, transaction, entry):
        return entry.date(transaction) >= self.date

class EndFilter(DateFilter):
    flag = "end"
    args = 1

    def __call__(self, transaction, entry):
        return entry.date(transaction) < self.date

class ExpressionFilter(Filter):
    flag = "filter"
    args = 1

    @classmethod
    def parse(cls, parser, expression):
        return cls(parser, expression)

    def __init__(self, parser, expression):
        self.parser = parser
        self.expression = compile(expression, "<commandline>", "eval")

    def __call__(self, transaction, entry):
        context = {
                "transaction" : SmartWrapper(transaction),
                "entry" : SmartWrapper(entry.of(transaction)),
                "date" : self.parse_date,
                "ZERO": ZERO }
        return eval(self.expression, context)

    def parse_date(self, str):
        return self.parser.parse_fuzzy_date(str)

class SmartWrapper(object):
    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, name):
        try:
            return getattr(self.obj, name)
        except AttributeError:
            return self.obj.get_tag(name)
