import functools
import inject
import logging
import requests

from requests import HTTPError

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()


LOG = logging.getLogger(__name__)
ALIASES = {
    'unassigned': 'assignee IS NULL',
    'unresolved': 'resolution IS NULL',
    'epic': '"epic link"',
}


def jqv(s):
    return "\"{}\"".format(jqe(s))


def jq_alias(s):
    for k, v in ALIASES.items():
        s = s.replace(k, v)
    return s


def jqk(s):
    return jq_alias(s)


def jqe(s):
    """JQL escape value
    :param s: a value
    """
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    return s


@inject.param('config')
def _with_auth(method, *args, config, **kwargs):
    kwargs = kwargs.copy()
    kwargs.setdefault('auth', (config.jira.username, config.jira.password))
    kwargs.setdefault('verify', config.jira.ssl_verify)
    return requests.request(method, *args, **kwargs)

http_get = functools.partial(_with_auth, 'GET')
http_post = functools.partial(_with_auth, 'POST')
http_put = functools.partial(_with_auth, 'PUT')


class RestClient(object):
    @inject.param('config')
    def assign(self, issue_id, username, config):
        url = "https://{base}/rest/api/2/issue/{id}/assignee".format(
            base=config.jira.host, id=issue_id
        )
        return http_put(url, json={"name": username})

    @inject.param('config')
    def get(self, issue_id, config):
        url = "https://{base}/rest/api/2/issue/{id}".format(
            base=config.jira.host, id=issue_id
        )
        return http_get(url).json()

    @inject.param('config')
    def transition(self, issue_id, transition, config):
        url = "https://{}/rest/api/2/issue/{}/transitions".format(
            config.jira.host, issue_id)

        transitions = http_get(url).json()
        transitions = {t['name']: t['id'] for t in transitions['transitions']}
        try:
            trans_id = transitions[transition]
        except KeyError:
            msg = '{t} is not available for {i}'.format(i=issue_id,
                                                        t=transition)
            raise Exception(msg)
        result = http_post(url, json={"transition": {"id": trans_id}})
        return result

    @staticmethod
    @inject.param('config')
    def find(*args, config, fields=('summary', 'status'), **kwargs):
        jql = ' AND '.join('%s=%s' % (jqk(k), jqv(v))
                           for k, v in kwargs.items())
        if args:
            jql = ' AND '.join(jq_alias(a) for a in args) + ' AND ' + jql
        jql += ' order by rank asc'
        LOG.debug("generated jql: %s", jql)
        url = "https://{}/rest/api/2/search".format(config.jira.host)
        result = http_get(url, params={'jql': jql, 'fields': ','.join(fields)})
        try:
            result.raise_for_status()
        except HTTPError:
            raise Exception(result.text)
        return result.json()['issues']
issue = RestClient()


class User(object):
    @inject.param('config')
    def get(self, username, config):
        url = "https://{}/rest/api/2/user".format(config.jira.host)
        return http_get(url, params={'username': username}).json()
user = User()
