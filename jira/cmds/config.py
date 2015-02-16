import inject
from getpass import getpass

from .. import api


class ConfigCommand(object):
    def __init__(self, subparsers):
        super().__init__()
        sub = subparsers.add_parser('setup',
                                    help='configure server and credentials')
        sub.add_argument('-s', '--show', action='store_true',
                         help='just show the configuration')
        sub.set_defaults(cmd=self.run)

    @staticmethod
    @inject.param('config')
    def run(args, config):
        if args.show:
            print('Server: ', config.jira.host)
            print('User: ', config.jira.username)
            return
        config.jira.host = input('Jira hostname: ')
        config.jira.username = input('Jira username: ')
        config.jira.password = getpass('Jira password: ')

        while True:
            test = input('Test new configuration [Y/n]:')
            if test.lower() in ['y', 'n']:
                if test == 'y':
                    user = api.user.get(config.username)
                    print('Seems you are good to go, %s' % user['displayName'])
                break

        config.save()


class PaletteCommand(object):
    def __init__(self, subparsers):
        super().__init__()
        sub = subparsers.add_parser('colors',
                                    help='shows a rainbow of console delight')
        sub.set_defaults(cmd=self.run)

    @staticmethod
    def run(args):
        for i in range(0, 256):
            print('\x1b[48;5;', i, 'm', i, sep='', end=' ')
