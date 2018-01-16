#!/usr/bin/env python3

import logging
from shlex import split
from subprocess import Popen, PIPE, STDOUT

from util import chunks

log = logging.getLogger(__name__)


def call(script, args):
    """
    Call script with args.
    :param script: The script
    :param args: The args
    :return: See run_command
    """
    cmd = [script] + args
    return run_command(' '.join(cmd))


def run_command(command, return_output=False, cwd=None):
    """
    Runs command.
    :param command: The command
    :param return_output: If True, returns output
    :param cwd: The directory to run in
    :return: return code and output (if return_output) as tuple
    """

    log.info('Running: %s', command)
    process = Popen(split(command), stdout=PIPE, stderr=STDOUT, cwd=cwd)
    the_output = []
    while True:
        output = process.stdout.readline().decode()
        if output == '' and process.poll() is not None:
            break
        if output:
            if return_output:
                the_output.append(output.replace('\n', ''))
            log.info(output.replace('\n', ''))
    rc = process.poll()
    if rc:
        raise SystemError(command)

    return (rc, ''.join(the_output)) if return_output else rc


def run_commands(commands, max_processes=10, cwd=None):
    """
    Runs commands in parallel processes.
    :param commands: The commands
    :param max_processes: The max number of parallel processes
    :param cwd: The directory to tun in
    :return: process (yielded)
    """
    if len(commands) > max_processes:
        for chunk in chunks(commands, max_processes):
            yield from run_commands(chunk, max_processes=max_processes, cwd=cwd)
    else:
        for process in [Popen(command, stdout=PIPE, stderr=STDOUT, shell=True, cwd=cwd) for command in commands]:
            yield process
