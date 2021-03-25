from .value import Value
from .tags import TagFilterable

class Entry(TagFilterable):
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

    def __repr__(self):
        return "<Entry %s>" % str(self)

    def __hash__(self):
        return hash((self.account, self.amount, tuple(sorted(self.tags.items()))))

    def date(self, transaction):
        result = self.get_tag("date")
        if result is None:
            result = transaction.date
        return result

    def of(self, transaction):
        result = Entry(self.account, self.amount, self.tags)
        result.date = self.date(transaction)
        result.parent = transaction
        return result

    @classmethod
    def from_entry(cls, transaction, entry):
        return entry
