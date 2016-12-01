#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = [
    'click',
    'messytables',
    'sqlalchemy',
    'psycopg2',
    'jinja2'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='csvloader',
    version='0.1.0',
    description='A csv uploader tool to RDMS',
    long_description=readme + '\n\n' + history,
    author="Wen Li",
    author_email='wen.li@ucl.ac.uk',
    url='https://github.com/spacelis/csv-loader',
    packages=[
        'csvloader',
    ],
    package_dir={'csvloader':
                 'csvloader'},
    entry_points={
        'console_scripts': [
            'cl-struct=csvloader.structing:console',
            'cl-upload=csvloader.dataloader:console',
            'cl-index=csvloader.indexbuilder:console'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='csv',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
