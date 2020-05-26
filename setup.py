import os
from setuptools import setup, find_packages

here = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(here, "README.md")) as f:
    long_description = f.read()

ext_dir_0 = os.path.join(here, "inkscape_extensions", "0.x")
ext_dir_1 = os.path.join(here, "inkscape_extensions", "1.x")

ext_files_0 = [
    os.path.join("inkscape_extensions", "0.x", fname)
    for fname in os.listdir(ext_dir_0)
    if fname.endswith(".inx") or fname.endswith(".py")
]

ext_files_1 = [
    os.path.join("inkscape_extensions", "1.x", fname)
    for fname in os.listdir(ext_dir_1)
    if fname.endswith(".inx") or fname.endswith(".py")
]

setup(
    name="figurefirst",
    version="0.0.6",
    author="Floris van Breugel, Theodore Lindsay, Peter Weir",
    author_email="floris@caltech.edu",
    packages=find_packages(exclude=("inkscape_extensions", "test")),
    install_requires=[
        "numpy",
        "matplotlib",
        "dill",
        "backports.functools_lru_cache; python_version<'3.3'",
    ],
    include_package_data=True,
    license="BSD",
    entry_points={
        "console_scripts": [
            "figurefirst_ext=figurefirst_scripts.install_inkscape_ext:main"
        ]
    },
    test_requires=["pytest", "tox"],
    data_files=[
        (os.path.join("inkscape_extensions", "0.x"), ext_files_0),
        (os.path.join("inkscape_extensions", "1.x"), ext_files_1),
    ],
    description="Matplotlib plotting stuff",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
