import os

from . import ioc
from .conf import Config


@ioc.provides('config')
def config(conf_file):
    return Config(conf_file)


@ioc.provides('render')
def renderer():
    from .table import prettify
    return prettify


ioc.value('conf_file', os.path.expanduser(
    '~/.local/share/com.simpoir.jira.client/settings.cfg'))
ioc.scan_modules('jira')
ioc.scan_modules('jira.cmds')


@ioc.provides('cli')
def run(parser, render, client, config):

    if not config.jira.host:
        from .cmds.config import ConfigCommand
        ConfigCommand().run()

    args = parser.parse_args()
    if args.issue:
        print(render(client.get(args.issue), mapping=[
            ('issue', 'key'),
            ('summary', 'fields.summary'),
            ('status', 'fields.status.name'),
            ('issue type', 'fields.issuetype.name'),
            ('reporter', 'fields.reporter.displayName'),
            ('assignee', 'fields.assignee.displayName'),
            ('link', 'self'),
        ]))
    else:
        from .cmds.config import PaletteCommand
        PaletteCommand().run()

if __name__ == '__main__':
    run()
