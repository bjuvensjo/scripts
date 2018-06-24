#!/usr/bin/env python3
import sys
import threading
from argparse import ArgumentParser
from glob import glob
from itertools import chain, count
from subprocess import Popen, PIPE, STDOUT
from time import sleep

import termios
from os import system

lock = threading.Lock()
action = None
play_process = None


def set_action(k, e):
    global action
    action = k
    e.set()


def stop():
    with lock:
        global play_process
        if play_process and play_process.poll() is None:
            try:
                play_process.kill()
            except SystemError:
                pass


def process_monitor(e):
    global play_process
    while True:
        with lock:
            if play_process and play_process.poll() is not None:
                set_action('n', e)
        sleep(1)


def play(track):
    global play_process
    stop()
    print('Playing', track)
    with lock:
        play_process = Popen(['afplay', track], stdout=PIPE, stderr=STDOUT)


def get_action(e):
    while True:
        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        try:
            c = sys.stdin.read(1)
            set_action(str(c), e)
        except IOError:
            pass

        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)


def play_all(tracks):
    global action
    tracks = sorted(tracks)
    keyed_tracks = list(
        zip(
            chain(range(97, 122), range(65, 90)),
            [s.split('/')[-1] for s in tracks]))

    e = threading.Event()
    threading.Thread(target=get_action, args=(e, ), daemon=True).start()
    index = 0
    threading.Thread(target=process_monitor, args=(e, ), daemon=True).start()
    play(tracks[index])
    while action != 's':
        e.wait()
        e.clear()
        if action == 'b':
            play(tracks[index])
        if action == 'c':
            print('Currently playing', tracks[index])
        if action == 'n':
            index = (index + 1) % len(tracks)
            play(tracks[index])
        if action == 'p':
            index = index - 1 if index > 0 else len(tracks) - 1
            play(tracks[index])
        if action == 's':
            stop()
        if action == 'l':
            system('clear')
            for i, p in keyed_tracks:
                print(chr(i), p)
            e.wait()
            e.clear()
            if action != chr(27): # Escape character
                for i, entry in zip(count(0), keyed_tracks):
                    if chr(entry[0]) == action:
                        index = i
                        play(tracks[index])
            action = ''

    print('Done!')


def get_audio_files(path):
    return glob('{}/**/*.wav'.format(path), recursive=True)


def parse_args(args):
    parser = ArgumentParser(description='Play wav files on Mac')
    parser.add_argument(
        '-d', '--dir', help='Directory containing Wav-files', default='.')
    return parser.parse_args(args)


def main(wav_dir):
    play_all(get_audio_files(wav_dir))


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    main(args.dir)
