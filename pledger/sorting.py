class MapSorting(object):
    def __init__(self, map):
        self.map = map

    def apply_to(self, list):
        l = [(self.map(x), x) for x in list]
        l.sort()
        return [x for (v, x) in l]
