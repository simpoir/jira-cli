from prettytable import PrettyTable
from .ioc import requires

BOLD = 1
FROM_PALETTE = 5
UNDERSCORE = 4
BG_COLOR = 48


def make_format(*values):
    def render(*args):
        return coloring.format(*args)
    coloring = '\x1b[' + ';'.join(map(str, values)) + 'm{}\x1b[m'
    return render
DEFAULT_FORMAT = make_format(BOLD)


@requires(conf='config')
class Table(PrettyTable):
    def __init__(self, *args, **kwargs):
        super(Table, self).__init__(*args, **kwargs)
        self.__odd = False
        self.row_odd = self.row_even = self.row_head = DEFAULT_FORMAT

    def set_conf(self, conf):
        self.row_odd = make_format(BG_COLOR, FROM_PALETTE,
                                   conf.style.row_odd)
        self.row_even = make_format(BG_COLOR, FROM_PALETTE,
                                    conf.style.row_even)
        self.row_head = make_format(BG_COLOR, FROM_PALETTE,
                                    conf.style.row_even, BOLD, UNDERSCORE)
    conf = property(fset=set_conf)

    def _stringify_header(self, options):
        head = super(Table, self)._stringify_header(options)
        return self.row_head(head)

    def _stringify_row(self, row, options):
        self.__odd = not self.__odd
        row = super(Table, self)._stringify_row(row, options)
        if self.__odd:
            return self.row_even(row)
        return self.row_odd(row)


def prettify_list(data):
    t = Table([])
    t.align[1] = 'l'
    for l in data:
        t.add_row(l)
    return t


def prettify_dict(data, mapping=None):
    t = Table(['Key', 'Value'])
    t.align['Key'] = 'l'
    t.align['Value'] = 'l'
    if mapping:
        for lbl, keys in mapping:
            keys = keys.partition('.')
            v = data[keys[0]]
            for k in keys[2].split('.'):
                if not k:
                    break
                v = v.get(k)
                if not v:
                    v = ''
                    break
            t.add_row([lbl, v])
    else:
        for l in data.items():
            t.add_row(l)
    return t


def prettify(obj, **kwargs):
    t = None
    if isinstance(obj, (list, tuple)):
        t = prettify_list(obj)
    elif isinstance(obj, dict):
        t = prettify_dict(obj, **kwargs)
    t.border = False
    return t
