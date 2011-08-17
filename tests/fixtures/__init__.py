import os.path

def fixture_path(base):
    return os.path.join(os.path.dirname(__file__), base)
