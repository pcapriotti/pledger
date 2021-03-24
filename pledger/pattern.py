from .filter import Filter
import re

class PatternParser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse_filter(self):
        last_operator = Filter.__or__
        result = None
        negated = False

        while self.has_tokens():
            token = self.get()
            if token == '(':
                filter = self.parse_filter()
                result = self.combine(result, filter, last_operator, negated)
                last_operator = Filter.__or__
                negated = False
            elif token == ')':
                return result
            elif token == 'and':
                last_operator = Filter.__and__
                negated = False
            elif token == 'or':
                last_operator = Filter.__or__
                negated = False
            elif token == 'not':
                negated = True
            else:
                filter = Filter.matches(re.compile(token))
                result = self.combine(result, filter, last_operator, negated)
                last_operator = Filter.__or__
                negated = False

        return result

    def combine(self, f1, f2, op, neg):
        if neg: f2 = ~f2
        if f1:
            return op(f1, f2)
        else:
            return f2

    def get(self):
        result = self.tokens[self.pos]
        self.pos += 1
        return result

    def has_tokens(self):
        return self.pos < len(self.tokens)
