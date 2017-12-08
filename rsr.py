#!/usr/bin/env python3

import os
import re


def rsr(root, excludes, from_pattern, to_pattern):
    for dir_path, dir_names, files in os.walk(root):
        if not any(d in excludes for d in dir_path.split('/')):
            for file in files:
                if file not in excludes:
                    content_changed = False
                    with open(os.path.join(dir_path, file), "tr", encoding="UTF-8") as old_file, \
                            open(os.path.join(dir_path, file) + ".tmp", "tw", encoding="UTF-8") as new_file:
                        for line in old_file:
                            new_line = re.sub(from_pattern, to_pattern, line)
                            content_changed = content_changed or new_line != line
                            new_file.write(new_line)
                    if content_changed:
                        os.replace(os.path.join(dir_path, file + ".tmp"), os.path.join(dir_path, file))
                    else:
                        os.remove(os.path.join(dir_path, file + ".tmp"))

                    if re.match(from_pattern, file):
                        os.rename(dir_path + '/' + file,
                                  dir_path + '/' + re.sub(from_pattern, to_pattern, file))

            for dir_name in dir_names:
                if dir_name not in excludes:
                    if re.match(from_pattern, dir_name):
                        os.rename(os.path.join(dir_path, dir_name),
                                  os.path.join(dir_path, re.sub(from_pattern, to_pattern, dir_name)))


topdir = '/Users/ei4577/slask/xx/ZESIN/integration/createpayment/v1_0'

rsr(topdir, ['.git'], "integration", "business")
rsr(topdir, ['.git'], "Integration", "Business")
rsr(topdir, ['.git'], "evry", "evryx")
