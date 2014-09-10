from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

tests_require = [
    'nose',
    'nose-cov',
    'mock',
    'jsonschema',
]

version = '0.0.0'
# TODO: read version number here


setup(
    name='balog',
    version=version,
    packages=find_packages(),
    install_requires=[
        'jsonschema',
        'structlog',
        'pytz',
        'iso8601',
        'coid',
    ],
    extras_require=dict(
        tests=tests_require,
    ),
    tests_require=tests_require,
    test_suite='nose.collector',
)
