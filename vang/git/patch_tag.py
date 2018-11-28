#!/usr/bin/env python3

from argparse import ArgumentParser
from os import makedirs
from re import match

from vang.pio.shell import run_command


def create_patch(repo, since_tag, tag, output):
    patch_dir = f'{output}/{tag}'
    makedirs(patch_dir)
    cmd = ' '.join([
        'git log -p --reverse --pretty=email --full-index --binary',
        '--stat',
        '-m',
        '--first-parent'
        f'{since_tag + ".." if since_tag else ""}{tag}',
        f'> {patch_dir}/tag.patch'
    ])
    print(cmd)
    rc, out = run_command(cmd, True, repo)
    return tag, patch_dir, out


def apply_patch(repo, tag, patch_dir):
    print('Apply patch', tag, patch_dir)
    return [
        run_command(cmd, True, repo) for cmd in [
            f'git apply {patch_dir}/*',
            'git add --all',
            f'git commit -m {tag}',
            f'git tag -a {tag} -m {tag}',
        ]
    ]


def get_tags(repo, tag_pattern):
    return [
        tag for tag in run_command('git tag', True, repo)[1].split('\n')
        if match(r'{}'.format(tag_pattern), tag)
    ]


def get_unpatched_tags(patchs_tags, applied_tags):
    return [p for p in patchs_tags if p not in applied_tags]


def is_valid(patchs_tags, applied_tags):
    return all([p == a for p, a in zip(patchs_tags, applied_tags)
                ]) and not len(applied_tags) > len(patchs_tags)


def main(patch_repo, tag_pattern, output, apply_repo):
    patchs_tags = get_tags(patch_repo, tag_pattern)
    applied_tags = get_tags(apply_repo, tag_pattern)
    if is_valid(patchs_tags, applied_tags):
        unpatched_tags = get_unpatched_tags(patchs_tags, applied_tags)
        patch_ranges = zip([None] + unpatched_tags, unpatched_tags)
        created_patches = [
            create_patch(patch_repo, since_tag, until_tag, output)
            for since_tag, until_tag in patch_ranges
        ]
        applied_patches = [
            apply_patch(apply_repo, tag, patch_dir)
            for tag, patch_dir, out in created_patches
        ]
        return applied_patches
    else:
        raise ValueError('Tags are not valid.')


def parse_args(args):
    parser = ArgumentParser(description='Create patches of tags and applies, ' +
                                        'commits and tags them in another repo.')
    parser.add_argument('tag_pattern', help='A tag pattern.')
    parser.add_argument('apply_repo', help='The repo to apply patches to.')
    parser.add_argument(
        '-p',
        '--patch_repo',
        help='The repo to patch from.',
        default='.',
    )
    parser.add_argument(
        '-o',
        '--output',
        help='A directory to put patches in.',
        default='./patch',
    )
    return parser.parse_args(args)
