#!/usr/bin/env python3

import logging
import sys
import traceback
from subprocess import PIPE, STDOUT, run
from typing import Tuple, Union, Iterable, Any

from vang.core.core import pmap_unordered

log = logging.getLogger(__name__)


def run_command(command: str,
                return_output: bool = False,
                cwd: str = None,
                check: bool = True,
                timeout: int = None) -> Tuple[int, Union[str, int]]:
    cp = run(
        command,
        cwd=cwd,
        stdout=PIPE,
        stderr=STDOUT,
        check=check,
        timeout=timeout,
        shell=True,
    )
    return (cp.returncode,
            cp.stdout.decode().strip()) if return_output else cp.returncode


def run_commands(commands_and_cwds: Iterable[Iterable[str]], max_processes: int = 10, check: bool = True,
                 timeout: int = None) -> Iterable[Any]:
    """
    Runs commands in parallel.

    :param commands_and_cwds: Pairs of command and working directory for the command
    :param max_processes: The max number of parallel processes
    :param check: Check for Exception
    :param timeout: The timeout of each process
    :return: CompletedProcess (yielded)
    """

    def f(cc):
        cmd, cwd = cc
        try:
            return run(
                cmd,
                cwd=cwd,
                stdout=PIPE,
                stderr=STDOUT,
                check=check,
                timeout=timeout,
                shell=True,
            )
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            raise e

    yield from pmap_unordered(
        f, commands_and_cwds, processes=max_processes, chunksize=1)
