import os
from configparser import RawConfigParser, NoOptionError


class ConfigSection(object):
    def __init__(self, conf, name):
        super().__init__()
        self._name = name
        self._conf = conf

    def __getattribute__(self, name):
        try:
            return super(ConfigSection, self).__getattribute__(name)
        except AttributeError:
            try:
                return super().__getattribute__('_conf').get(self._name, name)
            except NoOptionError as e:
                raise AttributeError(e)

    def __setattr__(self, name, value):
        try:
            conf = self._conf
            conf.get(self._name, name)
            return conf.set(self._name, name, value)
        except (NoOptionError, AttributeError):
            pass
        return super().__setattr__(name, value)


class Config(object):
    def __init__(self, conf_file):
        self._conf = RawConfigParser()
        self._file = conf_file
        self.jira = ConfigSection(self._conf, 'jira')
        self.style = ConfigSection(self._conf, 'style')
        self._conf.read_dict({
            'jira': {
                'host': '',
                'username': '',
                'password': '',
            },
            'style': {
                'row_even': 235,
                'row_odd': 239,
            },
        })
        self._conf.read(conf_file)

    def save(self):
        conf_path = os.path.dirname(self._file)
        if not os.path.isdir(conf_path):
            os.makedirs(conf_path)
        with open(self._file, 'w') as f:
            self._conf.write(f)
