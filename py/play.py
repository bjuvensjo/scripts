#!/usr/bin/env python3
from argparse import ArgumentParser
from glob import glob
from itertools import chain, count
from shlex import split
from subprocess import Popen, PIPE, STDOUT
from sys import argv

import sys
import termios


def get_char_keyboard():
    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    c = None
    try:
        c = sys.stdin.read(1)
    except IOError:
        pass

    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)

    return c


def execute(command, cwd=None):
    return Popen(split(command), stdout=PIPE, stderr=STDOUT, cwd=cwd)


def play(audio_file):
    print('Playing {}'.format(audio_file))
    return execute('afplay "{}"'.format(audio_file))


def get_audio_files(path):
    return glob('{}/**/*.wav'.format(path), recursive=True)


def play_list(playlist):
    sorted_playlist = sorted(playlist)
    keyed_playlist = list(
        zip(
            chain(range(97, 122), range(65, 90)),
            [s.split('/')[-1] for s in sorted_playlist]))
    process = play(sorted_playlist[0])
    i = 0
    do_play = True
    in_list = False
    while process:
        try:
            while do_play and process.poll() is None:
                c = get_char_keyboard()
                if c and in_list:
                    for index, entry in zip(count(0), keyed_playlist):
                        if chr(entry[0]) == c:
                            do_play = False
                            process.kill()
                            i = index - 1
                    print(c)
                    in_list = False
                    c = None
                if c == 'b' and not in_list:
                    do_play = False
                    process.kill()
                    i = max(-1, i - 1)
                if c == 'n' and not in_list:
                    do_play = False
                    process.kill()
                if c == 'p' and not in_list:
                    do_play = False
                    process.kill()
                    i = max(-1, i - 2)
                if c == 'l' and not in_list:
                    for i, p in keyed_playlist:
                        print(chr(i), p)
                    in_list = True
            i = min(len(sorted_playlist) - 1, i + 1)
            process = play(
                sorted_playlist[i]) if i < len(sorted_playlist) else None
            do_play = True
        except SystemExit:
            if process:
                process.kill()


def parse_args(args):
    parser = ArgumentParser(description='Play wav files on Mac')
    parser.add_argument(
        '-d', '--dir', help='Directory containing Wav-files', default='.')
    return parser.parse_args(args)


def main(wav_dir):
    play_list(get_audio_files(wav_dir))


if __name__ == '__main__':
    args = parse_args(argv[1:])
    main(args.dir)
