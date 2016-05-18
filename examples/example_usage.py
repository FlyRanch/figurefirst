
# coding: utf-8

# In[1]:

from pylab import *
#get_ipython().magic(u'pylab')


# ... add overview and an introductory use case.

# In[2]:

from figurefirst import FigureLayout,mpl_functions


# You can decorate the svg <figurefirsrt:axis> tag with mpl.axis methods. For example to call ax.axhspan(100,200,zorder=10,color ='r',alpha = 0.3) on the axis named frequency.22H05.start use the following tag:
# 
# ```
# <figurefirst:axis
#      figurefirst:name="frequency.22H05.start"
#      figurefirst:axhspan="100,200,zorder=10,color='r',alpha=.3"/> ```
#      
# The layout.apply_mpl_methods function will then apply the methods passing the value of the svg atribute as arguments to the mpl.axis method.

# In[20]:

#Passing axis methods
import numpy as np
layout = FigureLayout('axis_methods_layout.svg')
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
layout.apply_mpl_methods(layout.fig)
layout.insert_figures('mpl_panel_a')
layout.write_svg('axis_methods_test_output.svg')
close('all')


# It is also possible to add figurefirst attributes to groups. Providing the figurefirsrt:groupname = "mygroup" attribute will cause the enclosed figurefirst:axes elements to be added to the layout.axes_groups dictionary keyed by groupname, and then axis name. For instance, if the follwing group exists in svg:
# 
# ```
#   <g
#        style="display:inline"
#        transform="matrix(0.88667385,0,0,0.84804291,-1.1136586,117.0766)"
#        id="g3965-1"
#        figurefirst:groupname="oval">
#        <rect
#          y="34.986671"
#          x="70.899071"
#          height="42.857143"
#          width="594.55908"
#          id="rect2985-3-0"
#          style="fill:#008000">
#         <figurefirst:axis
#            figurefirst:name="circadian" />
#         </rect>
#    </g>
# ```
# python will expose the axis in ```layout.axes_groups['oval']['circadian']['axis']```. All axes that are not included in a group  will be collected into layout.axes_groups['none'].

# In[18]:

#Group axes example
layout = FigureLayout('group_axes_layout.svg')
layout.make_mplfigures()
layout.insert_figures()
layout.write_svg('group_axes_test_output.svg')
close('all')


# In[19]:

#Groups and figures example
layout = FigureLayout('multi_figures_layout.svg')
mplfig = layout.make_mplfigures()
layout.append_figure_to_layer(layout.figures.values()[0],'mpl_layer_2')
layout.append_figure_to_layer(layout.figures.values()[1],'mpl_layer_3')
layout.append_figure_to_layer(layout.figures.values()[2],'mpl_layer_4')
layout.write_svg('multi_fig_test_output.svg')
close('all')


# In[ ]:



