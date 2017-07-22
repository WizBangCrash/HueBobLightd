"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
from os import path
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open

HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='HueBobLightd',
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    # version='1.0.0',
    # Using https://github.com/pypa/setuptools_scm/ for automatic versioning
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='BobLight Server for Philips Hue Lights',
    long_description=LONG_DESCRIPTION,
    url='http://somewhere.com/BobHueLights.git',
    author='David Dix',
    author_email='david@dixieworld.co.uk',
    license='OpenSource MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers, Hobbyists',
        'Topic :: Software Development :: Build Tools',
        # Pick your license as you wish (should match "license" above)
        'License :: MIT Approved :: OpenSource',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
    ],
    keywords='boblightd philips-hue led tv',
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
        'jsmin>=2.2.0',
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
            'hueboblightd=HueBobLightd.hueboblightd:main',
            'lighteffects=HueBobLightd.lighteffects:main',
        ],
    },
    zip_safe=True,
)
