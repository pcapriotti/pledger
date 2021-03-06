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

from pledger.value import ZERO
from pledger.directive import Directive
from pledger.util import PledgerException
from pledger.tags import TagFilterable

class UnbalancedTransaction(PledgerException):
    def __init__(self, tr):
        self.tr = tr
        super(UnbalancedTransaction, self).__init__()

class UndefinedTransaction(PledgerException):
    def __init__(self, tr, index):
        self.tr = tr
        self.index = index
        super(UndefinedTransaction, self).__init__()

class Transaction(TagFilterable):
    def __init__(self, entries, date = None, label = "", tags = None):
        super(Transaction, self).__init__()
        self.entries = entries
        self.date = date
        self.label = label
        if tags: self.tags = tags
        undef = None
        balance = ZERO
        i = 0
        for e in self.entries:
            if e.amount is None:
                if undef: raise UndefinedTransaction(self, i)
                undef = e
            else:
                balance += e.amount
            i += 1
        if undef:
            undef.amount = -balance
        elif not balance.null():
            raise UnbalancedTransaction(self)

    def execute(self, processor):
        processor.add_transaction(self)

    def __repr__(self):
        return "Transaction (%s)" % self.date

    @classmethod
    def from_entry(cls, transaction, entry):
        return transaction

    @property
    def amount(self):
        result = ZERO
        for entry in self.entries:
            result += entry.amount
        return result

    def __getitem__(self, i):
        return self.entries[i]

    def __eq__(self, other):
        return self.entries == other.entries

    def clone(self):
        return self.__class__(self.entries, self.date, self.label, self.tags)

    @classmethod
    def account_tag_filter(cls, tag, value=None):
        def get_taggables(transaction, entry):
            return [e.account for e in transaction.entries]
        return cls.general_tag_filter(get_taggables, tag, value)
