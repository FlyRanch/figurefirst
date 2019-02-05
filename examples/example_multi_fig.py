#!/usr/bin/env python
from pylab import *
from figurefirst import FigureLayout,mpl_functions

print('running multi figure example')
#Groups and figures example
layout = FigureLayout('example_multi_fig_layout.svg')
mplfig = layout.make_mplfigures()
layout.append_figure_to_layer(layout.figures['threeport'],'mpl_layer_2')
layout.append_figure_to_layer(layout.figures['oval'],'mpl_layer_3')
layout.append_figure_to_layer(layout.figures['holy'],'mpl_layer_4')
layout.write_svg('example_multi_fig_output.svg')
close('all')
