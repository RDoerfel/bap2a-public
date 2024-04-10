from setuptools import find_packages, setup

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

setup(
    name="src",
    packages=find_packages(),
    version="0.1.0",
    python_requires=">=3.9",
    install_requires=REQUIREMENTS
)
