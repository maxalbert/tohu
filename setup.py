import versioneer

from setuptools import setup
from tohu import __version__

setup(
    name='tohu',
    description='Create random data in a controllable way.',
    author='Maximilian Albert',
    author_email='maximilian.albert@gmail.com',
    license='MIT',
    packages=['tohu'],
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    )
