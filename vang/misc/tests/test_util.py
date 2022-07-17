from operator import add

from pytest import raises

from vang.misc.util import chunks, thread_first, thread_last


def test_chunks():
    c = chunks(range(10), 5)
    assert list(next(c)) == [0, 1, 2, 3, 4]
    assert list(next(c)) == [5, 6, 7, 8, 9]
    with raises(StopIteration):
        next(c)


def test_thread_first():
    assert "abc" == thread_first("a", [add, "b"], [lambda x: x], [add, "c"])


def test_thread_last():
    assert "cba" == thread_last("a", [add, "b"], [lambda x: x], [add, "c"])
