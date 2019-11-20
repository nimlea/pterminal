# coding:utf-8
#! python3

from setuptools import setup, find_packages

setup(
    name = 'pipe-terminal',
    version = '1.0.0',
    description = 'A simple, light-weight input/output library for terminal in new thread',
    author = 'YL',
    url = 'https://github.com/yyyyl/pipe-terminal',
    packages = find_packages(),
    classifiers=[
		"License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
		"Programming Language :: Python :: 3",
    ],
)