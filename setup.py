from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='Twelfie!',
    version='0.0.0',
    description='A little script that tries to create a self-linking tweet.',
    author='Joe Friedl <joe@joefriedl.net>',
    pymodules=['twelfie'],
    install_requires=[
        'twitter==1.14.1',
    ],
    tests_require=[
        'pytest',
    ],
    cmdclass={'test': PyTest},
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Topic :: Artistic Software",
    ],
)
