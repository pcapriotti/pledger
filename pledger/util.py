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
        def __init__(self, **kwargs):
            for field in fields:
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
