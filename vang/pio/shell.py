#!/usr/bin/env python3

import logging
import traceback
from subprocess import PIPE, STDOUT, run

import sys

from vang.core.core import pmap_unordered

log = logging.getLogger(__name__)


def run_command(command, return_output=False, cwd=None, check=True, timeout=None):
    cp = run(command, cwd=cwd, stdout=PIPE, stderr=STDOUT, check=check, timeout=timeout, shell=True)
    return (cp.returncode, cp.stdout.decode().strip()) if return_output else cp.returncode


def run_commands(commands_and_cwds, max_processes=10, check=True, timeout=None):
    """
    Runs commands in parallel.
    :param commands_ands_cwds: Pairs of command and working directory for the command
    :param max_processes: The max number of parallel processes
    :param timeout: The timeout of each process
    :return: CompletedProcess (yielded)
    """

    def f(cc):
        cmd, cwd = cc
        try:
            return run(cmd, cwd=cwd, stdout=PIPE, stderr=STDOUT, check=check, timeout=timeout, shell=True)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            raise e

    yield from pmap_unordered(f, commands_and_cwds, processes=max_processes, chunksize=1)
