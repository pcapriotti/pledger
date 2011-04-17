def itersplit(p, it):
    elems = []
    for x in it:
        if p(x):
            yield elems
            elems = []
        else:
            elems.append(x)
