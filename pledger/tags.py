class Taggable(object):
    def __init__(self):
        self.tags = { }

    def has_tag(self, tag, value = None):
        if value is None:
            return self.tags.get(tag)
        else:
            return self.tags.get(tag) == value
