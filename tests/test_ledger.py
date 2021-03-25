def test_filename(parser, data_file):
    ledger = parser.parse_ledger(data_file("simple.dat"))
    assert ledger.absolute_filename("test.dat") == data_file("test.dat")
