#!/usr/bin/env python3
from datetime import datetime
from multiprocessing.dummy import Pool
from re import match


def create_timestamp():
    return datetime.now().strftime('%Y%m%dT%H%M%S.%f')


def has_match(s, regexps):
    return any((match(regexp, s) for regexp in regexps))


def is_included(name, excludes=None, includes=None):
    return not (excludes and has_match(name, excludes)) and (
        not includes or has_match(name, includes))


def pmap(f, iterable, chunksize=None, processes=25):
    with Pool(processes) as pool:
        return pool.map(f, iterable, chunksize)


def pmap_unordered(f, iterable, chunksize=1, processes=10):
    with Pool(processes=processes) as pool:
        completed_processes = pool.imap_unordered(
            f, iterable, chunksize=chunksize)
        for cp in completed_processes:
            yield cp


def select_keys(d, keys):
    return {k: v for k, v in d.items() if k in keys}
