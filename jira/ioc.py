"""Simple and effective inversion of control and dependency injection system.
"""
from functools import wraps
from itertools import chain

FACTORIES = {}
REGISTRY = {}

__ref = None


def value(name, value):
    """Convenience provider for non-factory providers
    :param name: the dependency name
    :param value: its value
    """
    provides(name)(lambda: value)


def provides(name):
    """Decorator for defining factories
    :param name: the component name
    """
    def wrapper(c):
        assert name not in FACTORIES, "duplicate provider for: {}".format(name)
        FACTORIES[name] = c
        return c
    return wrapper


def requires(*names, **mapping):
    """Cute decorator for defining dependencies
    :param *names: names of dependencies
    :param **mapping: keywords are treated as {dest: dep_name}
    """
    def wrapper(c):
        @wraps(c.__init__)
        def pre_init(self, *args, **kwargs):
            global __ref
            if __ref:
                REGISTRY.setdefault(__ref, self)
                __ref = None
            c.__pre_inject__(self, *args, **kwargs)
            # injection is guaranteed after __init__, in case of recursion
            for dst, name in chain([(n, n) for n in names], mapping.items()):
                dep = REGISTRY.get(name)
                if not dep:
                    try:
                        __ref = name
                        dep = REGISTRY.setdefault(name, FACTORIES[name]())
                    except KeyError:
                        assert False, 'unresolved dependency: {}'. format(name)
                setattr(self, dst, dep)
        c.__pre_inject__ = c.__init__
        c.__init__ = pre_init
        return c
    return wrapper
