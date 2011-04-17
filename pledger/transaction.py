class Transaction(object):
    def __init__(self, entries):
        self.entries = entries

    @property
    def amount(self):
        result = ZERO
        for entry in self.entries:
            result += entry.amount
        return result

    def __getitem__(self, i):
        return self.entries[i]
