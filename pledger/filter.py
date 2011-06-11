class Filter(object):
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

Filter.null = Filter(lambda transaction, entry: True)
