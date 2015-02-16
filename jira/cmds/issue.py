from ..api import issue
import inject


class ShowIssue(object):
    def __init__(self, subparsers):
        super().__init__()
        sub = subparsers.add_parser('show',
                                    help='show an issue')
        sub.add_argument('issue_id')
        sub.set_defaults(cmd=self.run)

    @staticmethod
    @inject.param('render')
    def run(args, render):
        print(render(issue.get(args.issue_id), mapping=[
            ('issue', 'key'),
            ('summary', 'fields.summary'),
            ('status', 'fields.status.name'),
            ('issue type', 'fields.issuetype.name'),
            ('reporter', 'fields.reporter.displayName'),
            ('assignee', 'fields.assignee.displayName'),
            ('link', 'self'),
        ]))
