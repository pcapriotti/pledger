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

class TagFilterable(Taggable):
    def __init__(self):
        super(TagFilterable, self).__init__()

    @classmethod
    def tag_filter(cls, tag, value = None):
        @Filter
        def result(transaction, entry):
            return cls.from_entry(transaction, entry).has_tag(tag, value)
        return result
