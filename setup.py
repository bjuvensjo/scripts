import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "vang",
    version = "0.5.0",
    author = "Magnus Bjuvensjö",
    author_email = "bjuvensjo@gmail.com",
    description = ("Scripts"),
    license = "MIT",
    keywords = "python artifactory bitbucket maven script stash",
    url = "https://github.com/bjuvensjo/scripts",
    packages=['vang.artifactory', 'vang.bitbucket', 'vang.core', 'vang.maven', 'vang.misc', 'vang.pio', 'vang.wildcat'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)