#!/usr/bin/env python3
from pytest import raises

from vang.misc.util import chunks


def test_chunks():
    c = chunks(range(10), 5)
    assert [0, 1, 2, 3, 4] == list(next(c))
    assert [5, 6, 7, 8, 9] == list(next(c))
    with raises(StopIteration):
        next(c)
