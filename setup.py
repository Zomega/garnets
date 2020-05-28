"""Setup script. Install garnets as a module, along with the CLI."""

from setuptools import find_packages
from setuptools import setup

with open('requirements.txt') as f:
    REQUIREMENTS = f.read().splitlines()

with open('README.md') as f:
    LONG_DESCRIPTION = f.read().strip()

setup(
    name='garnets',
    version='0.1.0',
    url='https://gitlab.com/Zomega/garnets',
    description='Port of StarGen (Stellar System Generator) to Python3.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author="Will Oursler",
    author_email="woursler@gmail.com",
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    keywords=[
        'StarGen',
        'planet',
        'solar system',
        'planet formation'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Intended Audience :: Other Audience',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
