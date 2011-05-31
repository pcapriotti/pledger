from pledger.entry import Entry
from pledger.tags import Taggable
from pledger.filter import Filter
from pledger.rule import Rule, Generator

class Account(Taggable):
    def __init__(self):
        super(Account, self).__init__()

    def __add__(self, value):
        return Entry(self, value)

    def __sub__(self, value):
        return Entry(self, -value)

    @classmethod
    def tag_filter(cls, tag, value = None):
        @Filter
        def result(transaction, entry):
            return entry.account.has_tag(tag, value)
        return result

    @classmethod
    def tag_rule(cls, tag):
        @Generator
        def generator(entry):
            return entry.account.tags[tag](entry)
        return Rule(cls.tag_filter(tag), generator)

class AccountRepository(object):
    def __init__(self):
        self.accounts = { }

    def get_account(self, name):
        account = self.accounts.get(name)
        if account is None:
            account = NamedAccount(name)
            self.accounts[name] = account
        return account

    def __getitem__(self, name):
        return self.get_account(name)

class NamedAccount(Account):
    def __init__(self, name):
        super(NamedAccount, self).__init__()
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.name

    def add_prefix(self, prefix):
        name = ":".join(prefix + [self.name])
        return NamedAccount(name)
