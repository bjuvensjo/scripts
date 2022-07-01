from operator import add

from pytest import raises

from vang.misc.util import chunks, thread_first, thread_last


def test_chunks():
    c = chunks(range(10), 5)
    assert [0, 1, 2, 3, 4] == list(next(c))
    assert [5, 6, 7, 8, 9] == list(next(c))
    with raises(StopIteration):
        next(c)


def test_thread_first():
    assert thread_first('a',
                        [add, 'b'],
                        [lambda x: x],
                        [add, 'c']) == 'abc'


def test_thread_last():
    assert thread_last('a',
                       [add, 'b'],
                       [lambda x: x],
                       [add, 'c']) == 'cba'
