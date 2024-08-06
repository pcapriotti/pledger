from .flag import FlagMetaclass
from .value import ZERO
from .tags import has_tag, get_tag


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

    @classmethod
    def tag(cls, factory, tag, value=None):
        @cls
        def result(transaction, entry):
            obj = factory.from_entry(transaction, entry)
            return has_tag(obj, tag, value)

        return result


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
        return cls(parser, expression, parser.repo)

    def __init__(self, parser, expression, repo):
        self.parser = parser
        self.expression = compile(expression, "<commandline>", "eval")
        self.repo = repo

    def __call__(self, transaction, entry):
        context = {
            "transaction": SmartWrapper(transaction),
            "entry": SmartWrapper(entry.info(transaction)),
            "date": self.parse_date,
            "ZERO": ZERO,
        }
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
            return get_tag(self.obj, name)
