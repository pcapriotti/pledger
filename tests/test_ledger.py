import os
import pytest

@pytest.fixture
def data_dir(request):
    return os.path.join(request.fspath.dirname, 'fixtures')

@pytest.fixture
def data_file(data_dir):
    def f(name):
        return os.path.join(data_dir, name)
    return f

def test_filename(parser, data_file):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    assert ledger.absolute_filename("test.dat") == data_file("test.dat")
