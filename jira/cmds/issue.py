from ..api import issue, worklog
import inject


class FindIssues(object):
    def __init__(self, subparsers):
        super().__init__()
        sub = subparsers.add_parser('find',
                                    help='find issues')
        sub.add_argument('filters', metavar='filter', nargs='*')
        sub.set_defaults(cmd=self.run)

    @staticmethod
    @inject.param('render')
    def run(args, render):
        filters = dict(f.split(':') for f in args.filters if ':' in f)
        args = [f for f in args.filters if ':' not in f]
        issues = issue.find(*args, **filters)
        rendered = render(
            issues,
            mapping=[
                ('issue', 'key'),
                ('status', 'fields.status.name'),
                ('summary', 'fields.summary'),
            ]
        )
        print(rendered)


class MyIssues(object):
    def __init__(self, subparsers):
        super().__init__()
        sub = subparsers.add_parser('my',
                                    help='show user issues')
        sub.set_defaults(cmd=self.run)

    @staticmethod
    @inject.param('config')
    @inject.param('render')
    def run(args, render, config):
        issues = issue.find(assignee=config.jira.username,
                            resolution='unresolved')
        rendered = render(
            issues,
            mapping=[
                ('issue', 'key'),
                ('status', 'fields.status.name'),
                ('summary', 'fields.summary'),
                ]
        )
        print(rendered)


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
        ]))


class Resolve(object):
    def __init__(self, subparsers):
        super().__init__()
        sub = subparsers.add_parser('resolve',
                                    help='resolve an issue')
        sub.add_argument('issue_id')
        sub.set_defaults(cmd=self.run)

    @staticmethod
    @inject.param('render')
    def run(args, render):
        issue.transition(args.issue_id, 'Resolve Issue')
        print(render(issue.get(args.issue_id), mapping=[
            ('issue', 'key'),
            ('summary', 'fields.summary'),
            ('status', 'fields.status.name'),
            ('issue type', 'fields.issuetype.name'),
            ('reporter', 'fields.reporter.displayName'),
            ('assignee', 'fields.assignee.displayName'),
            ]))


class Grab(object):
    def __init__(self, subparsers):
        super().__init__()
        sub = subparsers.add_parser('grab',
                                    help='grab an issue')
        sub.add_argument('issue_id')
        sub.set_defaults(cmd=self.run)

    @staticmethod
    @inject.param('render')
    @inject.param('config')
    def run(args, render, config):
        issue.assign(args.issue_id, config.jira.username)
        print(render(issue.get(args.issue_id), mapping=[
            ('issue', 'key'),
            ('summary', 'fields.summary'),
            ('status', 'fields.status.name'),
            ('issue type', 'fields.issuetype.name'),
            ('reporter', 'fields.reporter.displayName'),
            ('assignee', 'fields.assignee.displayName'),
            ]))


class Log(object):
    def __init__(self, subparsers):
        super().__init__()
        sub = subparsers.add_parser('log',
                                    help='shows and add worklog entries')
        sub.add_argument('issue_id')
        sub.add_argument('-t', '--time', help='a worklog entry (?h ?m)')
        sub.add_argument('-c', '--comment', help='adds comment to the entry')
        sub.set_defaults(cmd=self.run)

    @staticmethod
    @inject.param('render')
    @inject.param('config')
    def run(args, render, config):
        if args.comment and not args.time:
            print('Adding a timelog comment requires setting --time')
            return
        if args.time:
            worklog.add(args.issue_id,
                        comment=args.comment,
                        timeSpent=args.time)

        print(render(worklog.all(args.issue_id), mapping=[
            ('author', 'author.displayName'),
            ('date', 'started'),
            ('time spent', 'timeSpent'),
            ('comment', 'comment'),
        ]))
