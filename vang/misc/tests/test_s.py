from unittest.mock import call, patch

from pytest import raises

from vang.misc.s import get_cases
from vang.misc.s import get_split
from vang.misc.s import get_zipped_cases
from vang.misc.s import main
from vang.misc.s import parse_args


def test_get_split():
    assert ['foo', 'Bar', 'Baz'] == get_split('fooBarBaz')
    assert ['foo', 'Bar', 'Baz'] == get_split('foo_Bar_Baz')
    assert ['foo', 'Bar', 'Baz'] == get_split('foo-Bar-Baz')


def test_get_cases():
    cases = [
        'radioButton',
        'RadioButton',
        'radiobutton',
        'RADIOBUTTON',
        'radio_button',
        'RADIO_BUTTON',
        'radio-button',
        'RADIO-BUTTON',
    ]
    assert cases == get_cases('radioButton')
    assert cases == get_cases('RadioButton')
    assert cases == get_cases('radio_button')
    assert cases == get_cases('RADIO_BUTTON')
    assert cases == get_cases('radio-button')
    assert cases == get_cases('RADIO-BUTTON')


def test_zipped_cases():
    assert [
               ('foo',),
               ('Foo',),
               ('foo',),
               ('FOO',),
               ('foo',),
               ('FOO',),
               ('foo',),
               ('FOO',),
           ] == list(get_zipped_cases(['foo']))
    assert [
               ('foo', 'bar', 'baz'),
               ('Foo', 'Bar', 'Baz'),
               ('foo', 'bar', 'baz'),
               ('FOO', 'BAR', 'BAZ'),
               ('foo', 'bar', 'baz'),
               ('FOO', 'BAR', 'BAZ'),
               ('foo', 'bar', 'baz'),
               ('FOO', 'BAR', 'BAZ'),
           ] == list(get_zipped_cases(['foo', 'bar', 'baz']))


def test_parse_args():
    for args in [
        None, ''
    ]:
        with raises(SystemExit):
            parse_args(args.split(' ') if args else args)

    for args, pargs in [
        ['foo bar baz', {'strings': ['foo', 'bar', 'baz']}]
    ]:
        assert pargs == parse_args(args.split(' ') if args else []).__dict__


@patch('builtins.print')
def test_main(mock_print):
    main(['foo', 'bar'])
    assert [
               call('foo bar'),
               call('Foo Bar'),
               call('foo bar'),
               call('FOO BAR'),
               call('foo bar'),
               call('FOO BAR'),
               call('foo bar'),
               call('FOO BAR')
           ] == mock_print.mock_calls
