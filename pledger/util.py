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

def itersplit(p, it):
    elems = []
    for x in it:
        if p(x) and len(elems) > 0:
            yield elems
            elems = []
        else:
            elems.append(x)
    if len(elems) > 0:
        yield elems

class Observable(object):
    def __init__(self):
        self.listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    def fire(self, event, *args, **kwargs):
        for listener in self.listeners:
            method = None
            try:
                method = getattr(listener, "on_" + event)
            except AttributeError:
                pass
            if method:
                method(*args, **kwargs)

def struct(*fields):
    class tmp:
        def __init__(self, *args, **kwargs):
            for i in xrange(len(args)):
                setattr(self, fields[i], args[i])
            for field in fields:
                if field in kwargs:
                    setattr(self, field, kwargs[field])

        def __str__(self):
            return str(tuple(getattr(self, field) for field in fields))
    return tmp

def linearized(items):
    result = []
    for item, subitems in items:
        result.append(item)
        result += linearized(subitems)
    return result

class PledgerException(Exception):
    def __init__(self):
        super(PledgerException, self).__init__()
        self.line_number = None
        self.filename = None

    def __str__(self):
        return "%s (%s:%d)" % (self.__class__, self.filename, self.line_number)

class PrefixTree(object):
    def __init__(self, words = []):
        self.tree = { }
        for word in words:
            self.insert(word)

    def insert_aux(self, word, base, index):
        c = word[index : index + 1]
        sub = base.get(c)
        if sub is None:
            base[c] = word
        elif isinstance(sub, dict):
            self.insert_aux(word, sub, index + 1)
        elif sub != word:
            base[c] = { sub[index + 1 : index + 2] : sub }
            self.insert_aux(word, base, index)

    def insert(self, word):
        self.insert_aux(word, self.tree, 0)

    def from_prefix_aux(self, prefix, base, index):
        c = prefix[index:index+1]
        if c == '':
            return self.all_words(base)
        sub = base.get(c)

        if sub is None:
            return []
        elif isinstance(sub, dict):
            return self.from_prefix_aux(prefix, sub, index + 1)
        elif sub.startswith(prefix):
            return [sub]
        else:
            return []

    def from_prefix(self, prefix):
        return self.from_prefix_aux(prefix, self.tree, 0)

    def all_words(self, base):
        if isinstance(base, dict):
            result = []
            for sub in base.itervalues():
                result += self.all_words(sub)
            return result
        else:
            return [base]
