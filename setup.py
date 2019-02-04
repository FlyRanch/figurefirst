import os
from setuptools import setup

here = os.path.realpath(__file__)
ext_dir = os.path.join(os.path.dirname(here), 'inkscape_extensions')

ext_files = [
    os.path.join("inkscape_extensions", fname)
    for fname in os.listdir(ext_dir)
    if fname.endswith('.inx') or fname.endswith('.py')
]

setup(
    name='figurefirst',
    version='0.0.1',
    author='Floris van Breugel, Theodore Lindsay, Peter Weir',
    author_email='floris@caltech.edu',
    packages=['figurefirst', 'figurefirst.scripts'],
    install_requires=["numpy", "matplotlib", "dill"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "figurefirst_ext=figurefirst.scripts.install_inkscape_ext:main"
        ]
    },
    data_files=[("inkscape_extensions", ext_files)],
    description='Matplotlib plotting stuff',
    long_description=open('README.md').read(),
)
