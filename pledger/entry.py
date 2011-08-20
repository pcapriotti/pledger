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

from pledger.value import Value
from pledger.tags import Taggable

class Entry(Taggable):
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

    def __hash__(self):
        return hash(self.account, self.amount)

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
