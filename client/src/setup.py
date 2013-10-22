import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "python-mjf",
    version = "0.0.1",
    author = "Stefan Roiser",
    author_email = "Stefan Roiser at cern dot ch",
    description = ("An interface for easy access to host and job features"),
    license = "ASL2",
    keywords = "WLCG",
    url = "https://github.com/roiser/JobMachineFeatures",
    packages=['python-mjf'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: Apache 2 License",
    ],
)
