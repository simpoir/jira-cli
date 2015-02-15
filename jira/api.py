import requests
from .ioc import requires, provides

requests.packages.urllib3.disable_warnings()


@provides('client')
@requires(conf='config')
class RestClient(object):
    def get(self, issue_id):
        url = "https://{}/rest/api/2/issue/{}".format(self.conf.jira.host, issue_id)
        return requests.get(url, auth=(self.conf.jira.username, self.conf.jira.password),
                            verify=False).json()

@provides('jira_user')
@requires(conf='config')
class User(object):
    def get(self):
        url = "https://{}/rest/api/2/user".format(self.conf.jira.host)
        return requests.get(url, auth=(self.conf.jira.username, self.conf.jira.password),
                            params={'username': self.conf.jira.username},
                            verify=False).json()
