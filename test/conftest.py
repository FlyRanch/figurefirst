import pytest


def pytest_addoption(parser):
    parser.addoption("--keep_files", action="store_true", help="Do not clean up output files")
