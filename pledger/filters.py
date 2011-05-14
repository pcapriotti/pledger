from pledger.entry import Entry

class FilterCollection(object):
    def __init__(self):
        self.filters = { }

    def add_filter(self, filter, level = 0):
        self.filters.setdefault(level, [])
        self.filters[level].append(filter)

    def apply(self, transaction, account, amount):
        entries = [Entry(account, amount)]

        levels = self.filters.keys()
        levels.sort()

        for level in levels:
            filters = self.filters[level]
            new_entries = []
            for filter in filters:
                for entry in entries:
                    new_entries += filter.apply(transaction, entry)
            entries = new_entries

        return entries

class Filter(object):
    pass

class AccountFilter(Filter):
    def __init__(self, account):
        self.account = account

    def apply(self, transaction, entry):
        if entry.account == self.account:
            return [entry]
        else:
            return []
