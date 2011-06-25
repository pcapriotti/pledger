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
            return [cls.from_entry(transaction, entry)]
        return cls.general_tag_filter(get_taggables, tag, value)

    @classmethod
    def general_tag_filter(cls, get_taggables, tag, value=None):
        @Filter
        def result(transaction, entry):
            return any([x.has_tag(tag, value) for x in get_taggables(transaction, entry)])
        return result
