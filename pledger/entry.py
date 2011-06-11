from pledger.value import Value
from pledger.tags import Taggable

class Entry(Taggable):
    def __init__(self, account, amount, tags=None):
        super(Entry, self).__init__()
        self.account = account
        self.amount = amount
        if tags: self.tags = tags

    def __eq__(self, other):
        return self.account == other.account and \
               self.amount == other.amount

    def __str__(self):
        return "%s (%s)" % (self.account, self.amount)

    def date(self, transaction):
        result = self.get_tag("date")
        if result is None:
            result = transaction.date
        return result
