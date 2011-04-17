class Account(object):
    def __add__(self, value):
        return Entry(self, value)

    def __sub__(self, value):
        return Entry(self, -value)

class TopLevelAccount(Account):
    pass
