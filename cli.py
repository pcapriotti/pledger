from argparse import ArgumentParser
from pledger.report import reports
from pledger.filter import Filter
from pledger.parser import Parser
from pledger.sorting import MapSorting
from pledger.rule import RuleCollection
from pledger.template import default_template

parser = Parser()
filter = Filter.null
rules = RuleCollection()
sorting = MapSorting(lambda x: x.date)
template = default_template

def run_cli():
    argparser = ArgumentParser()
    argparser.add_argument("report", action="store")
    argparser.add_argument("--filename", action="store", nargs=1)

    args = argparser.parse_args()

    report_factory = reports.get(args.report)
    if report_factory is None:
        raise Exception("no such report " + args.report)

    ledger = parser.parse_ledger(open(args.filename[0]).read())
    report = report_factory(ledger, rules, filter, sorting)
    print template(report)
