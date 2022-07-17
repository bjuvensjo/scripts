from datetime import datetime
from unittest.mock import patch

import pytest

from vang.core.core import create_timestamp, get_in
from vang.core.core import has_match
from vang.core.core import is_included
from vang.core.core import pmap
from vang.core.core import pmap_unordered
from vang.core.core import select_keys


def test_create_timestamp():
    d = datetime(2007, 12, 6, 15, 29, 43, 79060)
    with patch("vang.core.core.datetime") as m:
        m.now.return_value = d
        assert create_timestamp() == "20071206T152943.079060"


def test_has_match():
    assert not has_match("foo", [])
    assert has_match("app.foo.bar", ["foo", "app.*", "bar"])
    assert not has_match("app.foo.bar", ["foo", ".*foox.*", "bar"])


def test_is_included():
    assert is_included("foo", None, None)
    assert is_included("foo", ["bar"], None)
    assert not is_included("foo", ["f.*"], None)
    assert is_included("foo", None, ["foo"])
    assert is_included("foo", None, ["f.*"])
    assert is_included("foo", ["bar"], ["foo"])
    assert not is_included("foo", ["foo"], ["foo"])


def test_pmap():
    assert pmap(lambda x: x * 2, [1, 2, 3]) == [2, 4, 6]


def test_pmap_unordered():
    assert sorted(pmap_unordered(lambda x: x * 2, [1, 2, 3])) == [2, 4, 6]


def test_select_keys():
    assert select_keys({"foo": 1, "bar": 2, "baz": 3}, ("foo", "bar")) == {
        "foo": 1,
        "bar": 2,
    }


@pytest.mark.parametrize(
    "keys, expected",
    [
        [["a"], {"b": {"c": "c", "d": [{"e": 1}]}}],
        [["a", "b", "c"], "c"],
        [["a", "b", "d", 0, "e"], 1],
    ],
)
def test_get_in(keys, expected):
    d = {"a": {"b": {"c": "c", "d": [{"e": 1}]}}}
    assert expected == get_in(d, keys)
