class Account(object):
    def __add__(self, value):
        return Entry(self, value)

    def __sub__(self, value):
        return Entry(self, -value)

    @classmethod
    def parse(cls, str):
        return NamedAccount(str)

class NamedAccount(Account):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self.name == other.name
