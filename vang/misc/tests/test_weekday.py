from vang.misc.weekday import name, zeller


def test_name():
    assert ['monday', 'thursday', 'thursday', 'sunday', 'tuesday', 'friday', 'sunday', 'wednesday', 'saturday',
            'monday', 'thursday', 'saturday'] == [name(d) for d in [1, 4, 4, 7, 2, 5, 7, 3, 6, 1, 4, 6]]


def test_zeller():
    assert [1, 4, 4, 7, 2, 5, 7, 3, 6, 1, 4, 6] == [zeller(2018, m, 1) for m in range(1, 13)]
