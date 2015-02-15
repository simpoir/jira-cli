from getpass import getpass

from ..ioc import provides, requires


@requires('config', 'jira_user')
class ConfigCommand(object):
    def run(self):
        self.config.jira.host = input('Jira hostname: ')
        self.config.jira.username = input('Jira username: ')
        self.config.jira.password = getpass('Jira password: ')

        test = None
        while True:
            test = input('Test new configuration [Y/n]:')
            if test.lower() in ['y', 'n']:
                if test == 'y':
                    user = self.jira_user.get()
                    print('Seems you are good to go, %s' % user['displayName'])
                break

        self.config.save()


class PaletteCommand(object):
    @staticmethod
    def run():
        for i in range(0, 256):
            print('\x1b[48;5;', i, 'm', i, sep='', end=' ')

