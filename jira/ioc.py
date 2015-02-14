"""Simple and effective inversion of control and dependency injection system.
"""
import inspect

from unittest import TestCase
from functools import wraps
from itertools import chain

FACTORIES = {}
REGISTRY = {}


def value(name, val):
    """Convenience provider for non-factory providers
    :param name: the dependency name
    :param val: its value
    """
    provides(name)(lambda: val)


def provides(name):
    """Decorator for defining factories
    :param name: the component name
    """
    def wrapper(c):
        assert name not in FACTORIES, "duplicate provider for: {}".format(name)
        if inspect.isfunction(c):
            @wraps(c)
            def func(*args, **kwargs):
                val = c(*_resolve_args(c, args), **kwargs)
                REGISTRY[name] = val
                return val
            FACTORIES[name] = func
            return func
        else:
            @wraps(c.__init__)
            def init(self, *args, **kwargs):
                REGISTRY.setdefault(name, self)
                return self.__post_register__(*args, **kwargs)
            c.__post_register__ = c.__init__
            c.__init__ = init
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
            c.__pre_inject__(self, *args, **kwargs)
            # injection is guaranteed after __init__, in case of recursion
            for dst, name in chain([(n, n) for n in names], mapping.items()):
                dep = _resolve(name)
                setattr(self, dst, dep)
        c.__pre_inject__ = c.__init__
        c.__init__ = pre_init
        return c
    return wrapper


def _resolve(name, stack=set()):
    dep = REGISTRY.get(name)
    if not dep:
        assert name not in stack, 'recursive reference to {}'.format(name)
        assert name in FACTORIES, \
            'unresolved dependency: {}'. format(name)
        stack.add(name)
        try:
            dep = REGISTRY.setdefault(name, FACTORIES[name]())
        finally:
            stack.remove(name)
    return dep


def _resolve_args(func, args):
    if args:
        return args
    args = [
        _resolve(arg)
        for arg in inspect.getargspec(func).args
        if arg != 'self'
    ]
    return args


class IocTests(TestCase):

    def setUp(self):
        super().setUp()
        # reset ioc
        global FACTORIES, REGISTRY
        FACTORIES = {}
        REGISTRY = {}

    def test_value(self):
        value('fooval', 42)

        @requires('fooval', mapped='fooval')
        class Obj(object):
            pass

        o = Obj()
        assert o.fooval == 42
        assert o.mapped == 42
        assert isinstance(o, Obj)

    def test_type(self):
        @provides('bar')
        class Bar(object):
            pass

        @requires('bar')
        class Foo(object):
            pass

        o = Foo()
        assert isinstance(o, Foo)
        assert isinstance(o.bar, Bar)

    def test_cyclic(self):
        @provides('bar')
        @requires('foo')
        class Bar(object):
            pass

        @provides('foo')
        @requires('bar')
        class Foo(object):
            pass

        o = Foo()
        assert o.bar.foo is o
        assert isinstance(o.bar, Bar)

    def test_args(self):
        value('foo', 42)

        @provides('bar')
        def bar(foo):
            return foo

        o = bar()
        assert o == 42

    def test_cyclic_factories(self):
        @provides('bar')
        def bar(foo):
            return foo

        @provides('foo')
        def foo(bar):
            return bar

        try:
            foo()
        except AssertionError:
            return
        assert False
