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
