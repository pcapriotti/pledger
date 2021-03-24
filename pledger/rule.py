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

import itertools


class RuleCollection(object):
    def __init__(self):
        self.rules = { }

    def add_rule(self, rule, level = 0):
        self.rules.setdefault(level, [])
        self.rules[level].append(rule)

    def apply(self, transaction, entry):
        entries = [entry]

        levels = list(self.rules.keys())
        levels.sort()

        for level in levels:
            rules = self.rules[level]
            new_entries = []
            for entry in entries:
                new_entries.append(entry)
                for rule in rules:
                    new_entries += list(rule.apply(transaction, entry))
            entries = new_entries

        return entries

class Generator(object):
    def __init__(self, generator):
        self.generator = generator

    def __call__(self, *args):
        return self.generator(*args)

    def __add__(self, other):
        @Generator
        def result(*args):
            return itertools.chain(self(*args), other(*args))
        return result
Generator.null = Generator(lambda *args: [])

class Rule(object):
    def __init__(self, filter, generator):
        self.filter = filter
        self.generator = generator

    def apply(self, transaction, entry):
        if self.filter(transaction, entry):
            return self.generator(entry.of(transaction))
        else:
            return []

class TransactionRule(Rule):
    def apply(self, transaction):
        if self.filter(transaction, None):
            return self.generator(transaction)
        else:
            return transaction
