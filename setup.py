from setuptools import setup, find_packages

setup(
    name="mpluspy",
    version="1.0.0",
    description="Client for Zetcom's Museum Plus API",
    packages=find_packages(),  # Automatically finds all packages
    install_requires=["requests", "pyaml"],
)
