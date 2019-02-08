import os
import glob
import fnmatch
import subprocess as sp
from contextlib import contextmanager

import pytest

example_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "examples")


def discover_examples():
    return glob.glob(os.path.join(example_dir, "example_*.py"))


def example_path_to_name(example_path):
    fname = os.path.split(example_path)[-1]
    base, _ = os.path.splitext(fname)
    prefix = "example_"
    if base.startswith(prefix):
        return base[len(prefix):]
    else:
        raise ValueError("{} does not start with expected prefix '{}'".format(example_path, prefix))


def get_file_set(root_dir, fname_match):
    out = set()
    for root, _, fnames in os.walk(root_dir):
        for fname in fnmatch.filter(fnames, fname_match):
            out.add(os.path.join(root, fname))
    return out


@contextmanager
def track_files(root_dir, delete=True):
    pattern = "example_*.svg"
    before = get_file_set(root_dir, pattern)
    yield
    if delete:
        after = get_file_set(root_dir, pattern)
        for fpath in after - before:
            os.remove(fpath)


@pytest.fixture
def context(request):
    initial_dir = os.getcwd()
    os.chdir(example_dir)
    with track_files(example_dir, delete=not request.config.getoption("--keep_files")):
        yield
    os.chdir(initial_dir)


@pytest.mark.parametrize("example_path", sorted(discover_examples()), ids=example_path_to_name)
def test_example(example_path, context):
    sp.check_call(["python", example_path])
