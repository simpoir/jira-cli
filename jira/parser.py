from argparse import ArgumentParser


def make_parser():
    parser = ArgumentParser(prog="jira")
    subparsers = parser.add_subparsers()

    from .cmds.config import ConfigCommand, PaletteCommand
    ConfigCommand(subparsers)
    PaletteCommand(subparsers)
    from .cmds.issue import ShowIssue, FindIssues, MyIssues, Resolve
    ShowIssue(subparsers)
    FindIssues(subparsers)
    MyIssues(subparsers)
    Resolve(subparsers)

    return parser
