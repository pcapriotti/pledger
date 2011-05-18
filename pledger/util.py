def itersplit(p, it):
    elems = []
    for x in it:
        if p(x):
            yield elems
            elems = []
        else:
            elems.append(x)

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
