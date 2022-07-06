#!/usr/bin/env python3
from functools import reduce


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i : i + n]


def thread_first(arg, *partials):
    """
    Works like Clojure thread first.
    Example 1:
    from operator import add
    thread_first('a',
                [add, 'b'],
                [lambda x: x],
                [add, 'c'])
    > 'abc'

    Example 2:
    from operator import add
    thread_first('abc',
                (str.replace, 'b', 'x'),
                (add, 'y'))
    > 'axcy'
    """
    return reduce(
        lambda mem, p: p[0](mem, *p[1:]) if len(p) > 1 else p[0](mem), partials, arg
    )


def thread_last(arg, *partials):
    """
    Works like Clojure thread last.
    Example:
    from operator import add
    thread_last('a',
                [add, 'b'],
                [lambda x: x],
                [add, 'c'])
    > 'cba'
    """
    return reduce(
        lambda mem, p: p[0](*p[1:], mem) if len(p) > 1 else p[0](mem), partials, arg
    )
