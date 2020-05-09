from setuptools import setup
from setuptools import find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='garnets',
    packages=find_packages(),
    install_requires=requirements,
)
