"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open

from os import path
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
name='PreConfig',
# Versions should comply with PEP440.  For a discussion on single-sourcing
# the version across setup.py and the project code, see
# https://packaging.python.org/en/latest/single_source_version.html
# version='1.0.0',
# Using https://github.com/pypa/setuptools_scm/ for automatic versioning
use_scm_version=True,
setup_requires=['setuptools_scm'],
description='Store preconfiguration',
long_description=long_description,
url='http://git.zbddisplays.local/PyPreConfig.git',
author='Displaydata Ltd',
author_email='david.dix@displaydata.com',
license='Commercial',
classifiers=[
# How mature is this project? Common values are
#   3 - Alpha
#   4 - Beta
#   5 - Production/Stable
'Development Status :: 3 - Alpha',
'Intended Audience :: Developers',
'Topic :: Software Development :: Build Tools',
# Pick your license as you wish (should match "license" above)
'License :: OSI Approved :: Commercial',
# Specify the Python versions you support here. In particular, ensure
# that you indicate whether you support Python 2, Python 3 or both.
'Programming Language :: Python :: 3.5',
'Programming Language :: Python :: 3.6',
    ],
keywords='production configuration esl logistics',
# You can just specify the packages manually here if your project is
# simple. Or you can use find_packages().
# packages=['PreConfig'],
packages=find_packages(exclude=['contrib',
                                'docs',
                                'tests']),
# For an analysis of "install_requires" vs pip's
# requirements files see:
# https://packaging.python.org/en/latest/requirements.html
install_requires=[
        'requests>=2.13.0',
        'grequests>=0.3.0',
        'openpyxl>=2.4.1',
        'jsmin>=2.2.0',
        'datetime>=4.0.0',
        'validators>=0.10'
    ],
# List additional groups of dependencies here (e.g. development
# dependencies). You can install these using the following syntax,
# for example:
# $ pip install -e .[dev,test]
extras_require={},
include_package_data=True,
# If there are data files included in your packages that need to be
# installed, specify them here.  If using Python 2.6 or less, then these
# have to be included in MANIFEST.in as well.
# package_data={
# 'PreConfig': ['package_data.dat'],
#     },
# Although 'package_data' is the preferred approach, in some case you may
# need to place data files outside of your packages. See:
# http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
# In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
# data_files=[('my_data', ['data/data_file'])],
# To provide executable scripts, use entry points in preference to the
# "scripts" keyword. Entry points provide cross-platform support and allow
# pip to create the appropriate form of executable for the target platform.
entry_points={
    'console_scripts': [
        'dc_config=PreConfig.dc_config:main',
        'dc_test_client=PreConfig.dc_test_client:main',
        'licensecmd=PreConfig.licensecmd:main',
        'preconfigure=PreConfig.preconfigure:main',
        'summaryreport=PreConfig.summaryreport:main',
        'add2store=PreConfig.add_to_store:main',
        'reserveblock=PreConfig.reserve_block:main',
    ],
},
zip_safe=True,
)
