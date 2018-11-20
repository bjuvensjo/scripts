#!/usr/bin/env python3

from argparse import ArgumentParser
from pprint import pprint
from re import match

from vang.pio.shell import run_command
from vang.pio.synchronize_dirs import synchronize_dirs


def apply_patch(patch_repo, apply_repo, ref):
    print('Apply patch', ref, patch_repo, apply_repo, ref)
    rc, output = run_command(f'git checkout {ref}', True, patch_repo)
    print(output)

    synchronize_dirs(patch_repo, apply_repo)
    rc, output = run_command('git status', True, apply_repo)
    print(output)

    if 'nothing to commit' in output:
        rc, output = run_command(f'git tag -a {ref} -m {ref}', True, apply_repo)
        print(output)
    else:
        for cmd in [
            'git add --all',
            f'git commit -m {ref}',
            f'git tag -a {ref} -m {ref}',
        ]:
            rc, output = run_command(cmd, True, apply_repo)
            print(output)

    return ref


def get_refs(repo, ref_pattern):
    return [
        ref for ref in run_command('git tag', True, repo)[1].split('\n')
        if match(r'{}'.format(ref_pattern), ref)
    ]


def get_unpatched_refs(patchs_refs, applied_refs):
    return [p for p in patchs_refs if p not in applied_refs]


def is_valid(patchs_refs, applied_refs):
    return all([p == a for p, a in zip(patchs_refs, applied_refs)
                ]) and not len(applied_refs) > len(patchs_refs)


def main(patch_repo, ref_pattern, apply_repo):
    patchs_refs = get_refs(patch_repo, ref_pattern)
    applied_refs = get_refs(apply_repo, ref_pattern)
    if is_valid(patchs_refs, applied_refs):
        unpatched_refs = get_unpatched_refs(patchs_refs, applied_refs)
        applied_patches = []
        for ref in unpatched_refs:
            apply_patch(patch_repo, apply_repo, ref)
            applied_patches.append(ref)
        return applied_patches
    else:
        raise ValueError('Tags are not valid.')


def parse_args(args):
    parser = ArgumentParser(description='Create patches of refs and applies, ' +
                                        'commits and refs them in another repo.')
    parser.add_argument('ref_pattern', help='A ref pattern.')
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


# rm -rf sign/patch; rm -rf lf-sign; md lf-sign; cd lf-sign; git init
# main(
#     '/Users/ei4577/slask/slask/PCS1806/sign',
#     'release.*',
#     '/Users/ei4577/slask/slask/PCS1806/lf-sign',
# )
# rm -rf lf-process.mortgage; md lf-process.mortgage; cd lf-process.mortgage; git init
the_applied_patches = main(
    '/Users/ei4577/slask/slask/PCS1806/process.mortgage',
    'release.*',
    '/Users/ei4577/slask/slask/PCS1806/lf-process.mortgage',
)
pprint(the_applied_patches)

# if __name__ == '__main__':  # pragma: no cover
#     args = parse_args(argv[1:])
#     main(args.patch_repo, args.ref_pattern, args.output, args.apply_repo)
