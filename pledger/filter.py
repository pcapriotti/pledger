from pledger.util import struct
from pledger.flag import FlagMetaclass
from pledger.value import ZERO

class Filter(object):
    __metaclass__ = FlagMetaclass
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
