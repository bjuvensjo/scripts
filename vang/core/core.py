#!/usr/bin/env python3
from datetime import datetime
from functools import reduce
from multiprocessing.dummy import Pool
from re import match
from typing import Callable, Iterable, Any, Dict, Mapping


def create_timestamp() -> str:
    return datetime.now().strftime('%Y%m%dT%H%M%S.%f')


def has_match(s: str, regexps: Iterable[str]) -> bool:
    return any((match(regexp, s) for regexp in regexps))


def is_included(name: str, excludes: Iterable[str] = None, includes: Iterable[str] = None) -> bool:
    return not (excludes and has_match(name, excludes)) and (not includes or has_match(name, includes))


def pmap(f: Callable[[Any], Any], iterable: Iterable[Any], chunksize: int = None, processes: int = 25) -> Iterable[Any]:
    with Pool(processes) as pool:
        return pool.map(f, iterable, chunksize)


def pmap_ordered(f: Callable[[Any], Any], iterable: Iterable[Any], chunksize: int = 1, processes: int = 10) -> Iterable[
    Any]:
    with Pool(processes=processes) as pool:
        completed_processes = pool.map(f, iterable, chunksize=chunksize)
        for cp in completed_processes:
            yield cp


def pmap_unordered(f: Callable[[Any], Any], iterable: Iterable[Any], chunksize: int = 1, processes: int = 10) -> \
        Iterable[Any]:
    with Pool(processes=processes) as pool:
        completed_processes = pool.imap_unordered(f, iterable, chunksize=chunksize)
        for cp in completed_processes:
            yield cp


def select_keys(d: Mapping[Any, Any], keys: Iterable[Any]) -> Dict[Any, Any]:
    return {k: v for k, v in d.items() if k in keys}


def get_in(seq, keys):
    return reduce(lambda mem, k: mem[k], keys, seq) or None
