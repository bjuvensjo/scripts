#!/usr/bin/env python3

import logging
from shlex import split
from subprocess import Popen, PIPE, STDOUT

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


def run_commands(commands_and_cwds, max_processes=10, timeout=None):
    """
    Runs commands in parallel processes.
    :param commands_ands_cwds: Pairs of command and working directory for the command
    :param max_processes: The max number of parallel processes
    :param timeout: The timeout of each process
    :return: process (yielded)
    """

    # TODO Handle timeout
    n = min(len(commands_and_cwds), max_processes)
    processes = [Popen(cc[0], stdout=PIPE, stderr=STDOUT, shell=True, cwd=cc[1]) for cc in commands_and_cwds[:n]]
    while processes:
        for rp in list(processes):
            if rp.poll() is not None:
                if n < len(commands_and_cwds):
                    cc = commands_and_cwds[n]
                    processes.append(Popen(cc[0], stdout=PIPE, stderr=STDOUT, shell=True, cwd=cc[1]))
                    n += 1
                processes.remove(rp)
                yield rp

    # Below is an alternative implementation that is somewhat simpler but somewhat slower.
    # if len(commands) > max_processes:
    #     for chunk in chunks(commands, max_processes):
    #         yield from run_commands(chunk, cwd=cwd, max_processes=max_processes, timeout=timeout)
    # else:
    #     for process in [Popen(command, stdout=PIPE, stderr=STDOUT, shell=True, cwd=cwd) for command in commands]:
    #         process.wait(timeout)
    #         yield process
