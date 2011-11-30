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

from pledger.rule import Rule, Generator
from pledger.filter import Filter

class Taggable(object):
    def __init__(self):
        self.tags = { }
        self.parent = None
        super(Taggable, self).__init__()

    def has_tag(self, tag, value = None):
        actual = self.get_tag(tag)
        if value is None:
            return actual is not None
        else:
            return value == actual

    def get_tag(self, tag):
        value = self.tags.get(tag)
        if value is None and self.parent:
            value = self.parent.get_tag(tag)
        return value

    def clone_with_tags(self, **tags):
        result = self.clone()
        for tag in tags:
            result.tags[tag] = tags[tag]
        return result

class TagFilterable(Taggable):
    def __init__(self):
        super(TagFilterable, self).__init__()

    @classmethod
    def tag_filter(cls, tag, value = None):
        def get_taggables(transaction, entry):
            taggable = cls.from_entry(transaction, entry)
            if taggable:
                return [taggable]
            else:
                return []
        return cls.general_tag_filter(get_taggables, tag, value)

    @classmethod
    def general_tag_filter(cls, get_taggables, tag, value=None):
        @Filter
        def result(transaction, entry):
            return any([x.has_tag(tag, value) for x in get_taggables(transaction, entry)])
        return result
