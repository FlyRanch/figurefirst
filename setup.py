from setuptools import setup

setup(
    name='figurefirst',
    version='0.0.1',
    author='Floris van Breugel, Theodore Lindsay, Peter Weir',
    author_email='floris@caltech.edu',
    packages=['figurefirst'],
    install_requires=["numpy", "matplotlib", "dill"],
    license='BSD',
    description='Matplotlib plotting stuff',
    long_description=open('README.md').read(),
)
