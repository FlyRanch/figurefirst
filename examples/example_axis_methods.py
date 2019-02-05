#!/usr/bin/env python
from pylab import *
from figurefirst import FigureLayout,mpl_functions

# You can decorate the svg <figurefirsrt:axis> tag with mpl.axis methods. For example to call ax.axhspan(100,200,zorder=10,color ='r',alpha = 0.3) on the axis named frequency.22H05.start use the following tag:
# 
# ```
# <figurefirst:axis
#      figurefirst:name="frequency.22H05.start"
#      figurefirst:axhspan="100,200,zorder=10,color='r',alpha=.3"/> ```
#      
# The layout.apply_mpl_methods function will then apply the methods passing the value of the svg atribute as arguments to the mpl.axis method.

#Passing axis methods
import numpy as np
layout = FigureLayout('example_axis_methods_layout.svg')
layout.make_mplfigures()
layout.fig.set_facecolor('None')
for mplax in layout.axes.values():
    ax = mplax['axis']
    ax.plot(np.arange(30),np.random.rand(30),color = 'k')
    mpl_functions.adjust_spines(ax,'none', 
                  spine_locations={}, 
                  smart_bounds=True, 
                  xticks=None, 
                  yticks=None, 
                  linewidth=1)
    ax.patch.set_facecolor('None')
layout.apply_mpl_methods()
layout.insert_figures('mpl_panel_a')
layout.write_svg('example_axis_methods_output.svg')
close('all')