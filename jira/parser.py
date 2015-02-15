from argparse import ArgumentParser

from .ioc import provides


@provides('parser')
class JiraParser(ArgumentParser):
    def __init__(self):
        super(JiraParser, self).__init__(prog="jira")
        self.add_argument('issue',
                          metavar='issue',
                          help="the issue number",
                          nargs="?")
