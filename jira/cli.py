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

    parser = make_parser()
    args = parser.parse_args()

    if not config.jira.host and not getattr(args, 'setup', False):
        print('This is all cute, but you have not configured me. Try "setup"')
        return

    if hasattr(args, 'cmd'):
        args.cmd(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    run()
