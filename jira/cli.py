import os
import inject

from .conf import Config
from .parser import make_parser


CONF_FILE = os.path.expanduser(
    '~/.local/share/com.simpoir.jira.client/settings.cfg'
)


def cli_config(binder):
    config = Config(CONF_FILE)
    binder.bind('config', config)
    from .table import prettify
    binder.bind('render', prettify)


def run():
    inject.configure(cli_config)

    config = inject.instance('config')

    if not config.jira.host:
        from .cmds.config import ConfigCommand
        ConfigCommand().run()

    parser = make_parser()
    args = parser.parse_args()

    try:
        args.cmd(args)
    except AttributeError:
        parser.print_help()


if __name__ == '__main__':
    run()
