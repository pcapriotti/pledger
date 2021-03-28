from .rule import Rule, Generator


def has_tag(obj, tag, value=None):
    actual = get_tag(obj, tag)
    if value is None:
        return actual is not None
    else:
        return value == actual


def get_tag(obj, tag):
    if obj is None:
        return None

    value = obj.tags.get(tag)
    if value is None and hasattr(obj, 'parent'):
        return get_tag(obj.parent, tag)
    else:
        return value
