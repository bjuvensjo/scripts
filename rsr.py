#!/usr/bin/env python3

import re
from os import remove, rename, replace, walk
from os.path import join


def rsr(root, excludes, from_pattern, to_pattern):
    for dir_path, dir_names, files in walk(root):
        if not any(d in excludes for d in dir_path.split('/')):
            for file in files:
                if file not in excludes:
                    content_changed = False
                    with open(join(dir_path, file), "tr", encoding="UTF-8") as old_file, \
                            open(join(dir_path, file + ".tmp"), "tw", encoding="UTF-8") as new_file:
                        for line in old_file:
                            new_line = re.sub(from_pattern, to_pattern, line)
                            content_changed = content_changed or new_line != line
                            new_file.write(new_line)
                    if content_changed:
                        replace(join(dir_path, file + ".tmp"), join(dir_path, file))
                    else:
                        remove(join(dir_path, file + ".tmp"))

                    if re.match(from_pattern, file):
                        rename(join(dir_path, file),
                               join(dir_path, re.sub(from_pattern, to_pattern, file)))

            for dir_name in dir_names:
                if dir_name not in excludes:
                    if re.match(from_pattern, dir_name):
                        rename(join(dir_path, dir_name),
                               join(dir_path, re.sub(from_pattern, to_pattern, dir_name)))


topdir = '/Users/ei4577/slask/xx/ZESIN/integration/createpayment/v1_0'

rsr(topdir, ['.git'], "integration", "business")
rsr(topdir, ['.git'], "Integration", "Business")
rsr(topdir, ['.git'], "evry", "evryx")
