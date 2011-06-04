class Taggable(object):
    def __init__(self):
        self.tags = { }
        super(Taggable, self).__init__()

    def has_tag(self, tag, value = None):
        if value is None:
            return tag in self.tags
        else:
            return self.tags.get(tag) == value
