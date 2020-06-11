from . import svg_to_axes

# reload(svg_to_axes)
from . import mpl_functions
from .svg_to_axes import FigureLayout
from . import mpl_fig_to_figurefirst_svg
from . import svg_util
from . import deprecated_regenerate

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
