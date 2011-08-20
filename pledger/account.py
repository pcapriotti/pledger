# Copyright (C) 2011 by Paolo Capriotti <p.capriotti@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from pledger.entry import Entry
from pledger.tags import TagFilterable, Taggable
from pledger.filter import Filter
from pledger.rule import Rule, Generator

class AccountBase(object):
    def __init__(self):
        super(AccountBase, self).__init__()
        self.parent = None
        self.base_name = None

class Account(AccountBase, TagFilterable):
    def __init__(self):
        super(Account, self).__init__()

    def __add__(self, value):
        return Entry(self, value)

    def __sub__(self, value):
        return Entry(self, -value)

    @classmethod
    def from_entry(cls, transaction, entry):
        return entry.account

    @classmethod
    def tag_rule(cls, tag, filter = Filter.null):
        @Generator
        def generator(entry):
            return entry.account.get_tag(tag)(entry)
        return Rule(cls.tag_filter(tag) & filter, generator)

    def root(self):
        if self.parent and self.parent.name:
            return self.parent.root()
        else:
            return self

    def shortened_name(self, size):
        full = self.name
        delta = len(full) - size
        if delta <= 0: return full
        components = self.name_components()
        n = len(components) - 1
        component_delta = delta / n
        extra = delta - component_delta * n
        components = \
            [x[:len(x) - component_delta - 1] for x in components[:extra]] + \
            [x[:len(x) - component_delta] for x in components[extra:-1]] + \
            [components[-1]]
        return ":".join(components)

    def name_components(self):
        if self.parent and self.parent.name:
            return self.parent.name_components() + [self.base_name]
        else:
            return [self.base_name]

    @property
    def name(self):
        return ":".join(self.name_components())

    def is_ancestor(self, account):
        if self == account:
            return True
        elif account.parent and account.parent.name:
            return self.is_ancestor(account.parent)
        else:
            return False

    def filter(self):
        @Filter
        def result(transaction, entry):
            return self.is_ancestor(entry.account)
        return result

class AccountRepository(AccountBase, Taggable):
    def __init__(self):
        super(AccountRepository, self).__init__()
        self.accounts = { }

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

    def sub_name(self, account):
        def sub_name_components(account):
            if account == self:
                return []
            elif account.parent.base_name is None:
                return None
            else:
                return sub_name_components(account.parent) + [account.base_name]
        components = sub_name_components(account)
        if components:
            return ":".join(components)

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
