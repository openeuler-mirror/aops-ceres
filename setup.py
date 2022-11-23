# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "aops-ceres"
VERSION = "2.0.0"

INSTALL_REQUIRES = [
    "flask",
    "flask-testing",
    "jsonschema",
    "requests",
    "libconf",
    "connexion",
    "swagger-ui-bundle>=0.0.2",
    "concurrent_log_handler"
]

setup(
    name=NAME,
    version=VERSION,
    description="ApplicationTitle",
    author_email="",
    url="",
    keywords=["Swagger", "A-Ops ceres"],
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    data_files=[
        ('/etc/aops', ['conf/ceres.conf']),
        ('/usr/lib/systemd/system', ['aops-ceres.service']),
    ],
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['aops-ceres=ceres.__main__:main']},
    long_description="""\
    GroupDesc
    """
)
