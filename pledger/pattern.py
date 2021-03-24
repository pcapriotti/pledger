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
