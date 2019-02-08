import os
from setuptools import setup, find_packages

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
    packages=find_packages(exclude=("inkscape_extensions", "test")),
    install_requires=["numpy", "matplotlib", "dill"],
    include_package_data=True,
    license='BSD',
    entry_points={
        "console_scripts": [
            "figurefirst_ext=figurefirst_scripts.install_inkscape_ext:main"
        ]
    },
    test_requires=["pytest", "scipy", "tox"],
    data_files=[("inkscape_extensions", ext_files)],
    description='Matplotlib plotting stuff',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown"
)
