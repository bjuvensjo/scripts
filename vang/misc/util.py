#!/usr/bin/env python3
from functools import reduce


def chunks(seq, n):
    """Yield successive n-sized chunks from seq."""
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def thread_first(arg, *partials):
    """
    Works like Clojure thread first.

    >>> from operator import add
    >>> thread_first('a',
    ...     [add, 'b'],
    ...     [lambda x: x],
    ...     [add, 'c'])
    'abc'

    >>> from operator import add
    >>> thread_first('abc',
    ...     (str.replace, 'b', 'x'),
    ...     (add, 'y'))
    'axcy'
    """
    return reduce(
        lambda mem, p: p[0](mem, *p[1:]) if len(p) > 1 else p[0](mem), partials, arg
    )


def thread_last(arg, *partials):
    """
    Works like Clojure thread last.

    >>> from operator import add
    >>> thread_last('a',
    ...     [add, 'b'],
    ...     [lambda x: x],
    ...     [add, 'c'])
    'cba'
    """
    return reduce(
        lambda mem, p: p[0](*p[1:], mem) if len(p) > 1 else p[0](mem), partials, arg
    )
