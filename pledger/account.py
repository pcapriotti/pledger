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
        self.parent = None
        self.base_name = None
        super(AccountRepository, self).__init__()

    def get_account(self, name, *args):
        account = self.accounts.get(name)
        if account is None:
            account = self.create_subaccount(name)
            self.accounts[name] = account
        if len(args):
            return account.get_account(*args)
        else:
            return account

    def __getitem__(self, name):
        components = name.split(":")
        return self.get_account(*components)

    def create_subaccount(self, name):
        return NamedAccount(name, self)

    def get_tag(self, tag):
        pass

    @property
    def name(self):
        pass

class NamedAccount(Account, AccountRepository):
    def __init__(self, name, parent = None):
        super(NamedAccount, self).__init__()
        self.base_name = name
        self.parent = parent

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<%s>" % self.name

    def __cmp__(self, other):
        if other:
            return cmp(self.name, other.name)
        else:
            return 1

    @property
    def name(self):
        parent_name = None
        if self.parent is not None:
            parent_name = self.parent.name

        if parent_name is None:
            return self.base_name
        else:
            return parent_name + ":" + self.base_name
