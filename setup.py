import versioneer

from setuptools import setup, find_packages
from codecs import open
from os import path
from tohu import __version__

here = path.abspath(path.dirname(__file__))

# Read long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tohu',
    version=versioneer.get_version(),
    description='Create random data in a controllable way',
    long_description=long_description,
    url='https://github.com/maxalbert/tohu',
    author='Maximilian Albert',
    author_email='maximilian.albert@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    install_requires=['mako', 'pandas', 'sqlalchemy', 'tqdm'],
    extras_require={
        'dev': ['ipython', 'jupyter'],
        'test': ['pytest', 'nbval'],
    },
    cmdclass=versioneer.get_cmdclass(),
    )
