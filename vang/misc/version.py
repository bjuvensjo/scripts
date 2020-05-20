import re
from itertools import count


def _get_rc_number(version):
    m = re.search(r'rc([0-9]+)', version)
    return int(m[1]) if m else -1


def _get_version_number(version):
    version = version.replace('_', '.')
    try:
        numbers = [int(x) for x in re.match(r'([0-9]+)\.([0-9]+)\.([0-9]+)', version).groups()]
        return numbers
    except AttributeError as e:
        raise ValueError(f'version must be semver {version}')


def _get_max(versions):
    if not versions:
        return None
    version_numbers = [_get_version_number(v) for v in versions]
    if len(version_numbers) == 1:
        return versions[0]
    max_version = versions[0]
    max_version_number = version_numbers[0]
    for i, v in zip(count(1), version_numbers[1:]):
        new_max = True
        if v[0] < max_version_number[0]:
            new_max = False
        if v[0] == max_version_number[0]:
            if v[1] < max_version_number[1]:
                new_max = False
            if v[1] == max_version_number[1]:
                if v[2] < max_version_number[2]:
                    new_max = False
        if new_max:
            max_version = versions[i]
            max_version_number = v
    if 'rc' not in max_version:
        return max_version
    else:
        max_rc = max(_get_rc_number(v) for v in versions if _get_version_number(v) == max_version_number)
        return next(v for v in versions if _get_rc_number(v) == max_rc and _get_version_number(v) == max_version_number)


def get_latest_snapshot(versions):
    filtered_versions = [v for v in versions if 'snapshot' in v.lower() and 'rc' not in v.lower()]
    return _get_max(filtered_versions)


def get_latest_rc(versions):
    filtered_version = [v for v in versions if 'rc' in v.lower()]
    return _get_max(filtered_version)


def get_latest_fixed(versions):
    filtered_versions = [v for v in versions if 'rc' not in v.lower() and 'snapshot' not in v.lower()]
    return _get_max(filtered_versions)

