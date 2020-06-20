#!/usr/bin/env python
from pylab import *
from figurefirst import FigureLayout, mpl_functions

# Group axes example
layout = FigureLayout("example_group_axes_layout.svg")
layout.make_mplfigures()
layout.insert_figures()
layout.write_svg("example_group_axes_output.svg")
close("all")
