import inject
import requests

requests.packages.urllib3.disable_warnings()


class RestClient(object):
    @inject.param('config', 'config')
    def get(self, issue_id, config):
        url = "https://{}/rest/api/2/issue/{}".format(config.jira.host, issue_id)
        return requests.get(url, auth=(config.jira.username, config.jira.password),
                            verify=False).json()
issue = RestClient()


class User(object):
    @inject.param('config', 'config')
    def get(self, config):
        url = "https://{}/rest/api/2/user".format(config.jira.host)
        return requests.get(url, auth=(config.jira.username, config.jira.password),
                            params={'username': config.jira.username},
                            verify=False).json()
user = User()
