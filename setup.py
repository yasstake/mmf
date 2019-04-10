from setuptools import setup
from setuptools import find_packages

setup(
    name="dl",
    version="0.1.0",
    install_requires=['tensorflow', "scipy"],
    packages=['dl', 'log', 'gcp']
)