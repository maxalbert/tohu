import versioneer

from setuptools import setup
from randdict import __version__

setup(
    name='randdict',
    description='Create random data in a controllable way.',
    author='Maximilian Albert',
    author_email='maximilian.albert@gmail.com',
    license='MIT',
    packages=['randdict'],
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    )
