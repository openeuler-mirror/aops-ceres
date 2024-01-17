# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "aops-ceres"
VERSION = "1.3.2"

INSTALL_REQUIRES = ["jsonschema", "requests", "libconf", "concurrent_log_handler"]

setup(
    name=NAME,
    version=VERSION,
    description="ApplicationTitle",
    author_email="",
    url="",
    keywords=["A-Ops ceres"],
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    data_files=[('/etc/aops', ['conf/ceres.conf']), ('/opt/aops', ['conf/register_example.json'])],
    entry_points={'console_scripts': ['aops-ceres=ceres.main:main']},
    long_description="""\
    GroupDesc
    """,
)
