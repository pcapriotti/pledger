from pledger.value import Value
from pledger.tags import Taggable

class Entry(Taggable):
    def __init__(self, account, amount):
        super(Entry, self).__init__()
        self.account = account
        self.amount = amount

    def __eq__(self, other):
        return self.account == other.account and \
               self.amount == other.amount

    def __str__(self):
        return "%s (%s)" % (self.account, self.amount)
