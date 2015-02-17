import inject
import logging
import requests

from requests import HTTPError

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()


LOG = logging.getLogger(__name__)
ALIASES = {
    'unassigned': 'assignee IS NULL',
    'epic': 'epic link',
}


def jqv(s):
    return "\"{}\"".format(jqe(s))


def jqe(s):
    """JQL escape value
    :param s: a value
    """
    for k, v in ALIASES.items():
        s = s.replace(k, v)
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    return s


class RestClient(object):
    @inject.param('config')
    def get(self, issue_id, config):
        url = "https://{}/rest/api/2/issue/{}".format(config.jira.host, issue_id)
        return requests.get(url, auth=(config.jira.username, config.jira.password),
                            verify=False).json()

    @inject.param('config')
    def transition(self, issue_id, transition, config):
        url = "https://{}/rest/api/2/issue/{}/transitions".format(
            config.jira.host, issue_id)
        auth = (config.jira.username, config.jira.password)
        transitions = requests.get(url, auth=auth, verify=False).json()
        transitions = {t['name']: t['id'] for t in transitions['transitions']}
        try:
            trans_id = transitions[transition]
        except KeyError:
            msg = '{t} is not available for {i}'.format(i=issue_id,
                                                        t=transition)
            raise Exception(msg)
        result = requests.post(url, auth=auth,
                               json={"transition": {"id": trans_id}},
                               verify=False)
        return result

    @staticmethod
    @inject.param('config')
    def find(*args, config, fields=('summary', 'status'), **kwargs):
        jql = ' AND '.join('%s=%s' % (jqv(k), jqv(v))
                           for k, v in kwargs.items())
        if args:
            jql = ' AND '.join(jqe(a) for a in args) + ' AND ' + jql
        jql += ' order by rank asc'
        LOG.debug("generated jql: %s", jql)
        url = "https://{}/rest/api/2/search".format(config.jira.host)
        result = requests.get(url,
                              auth=(config.jira.username, config.jira.password),
                              params={'jql': jql, 'fields': ','.join(fields)},
                              verify=False)
        try:
            result.raise_for_status()
        except HTTPError:
            raise Exception(result.text)
        return result.json()['issues']
issue = RestClient()


class User(object):
    @inject.param('config')
    def get(self, user, config):
        url = "https://{}/rest/api/2/user".format(config.jira.host)
        return requests.get(url, auth=(config.jira.username, config.jira.password),
                            params={'username': user},
                            verify=False).json()
user = User()
