__all__ = [
    "svg_to_axes",
    "mpl_functions",
    "mpl_fig_to_figurefirst_svg",
    "svg_util",
    "deprecated_regenerate",
    "FigureLayout",
]

from figurefirst.svg_to_axes import FigureLayout

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError

import sys

if sys.version_info[0] > 2:  # regenerate uses importlib.utils, which requires python 3?
    from . import regenerate

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    print("package not installed")
