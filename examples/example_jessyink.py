import numpy as np
from figurefirst import FigureLayout

layout = FigureLayout('jessyink_layout.svg')
layout.make_mplfigures()

x_data = np.arange(30)

ax = layout.axes['ax_name']['axis']
ax.plot(x_data, x_data**3, color='k', gid='figurefirst:line1')
ax.fill_between(x_data, .5*x_data**3, 2*x_data**3, color='k', edgecolor='none', alpha=.3, gid='figurefirst:fill1')
ax.plot(x_data, x_data[::-1]**3, color='r', gid='figurefirst:line2')
ax.axvspan(2, 10, color='b', alpha=.2, gid='figurefirst:span1')

layout.apply_mpl_methods()
layout.insert_figures('figurefirst_target_layer')

layout.pass_xml('figurefirst:span1','jessyink:effectIn', 'name:appear;order:1;length:800')
layout.pass_xml('figurefirst:line1','jessyink:effectIn', 'name:appear;order:2;length:800')
layout.pass_xml('figurefirst:fill1','jessyink:effectIn', 'name:appear;order:2;length:800')
layout.pass_xml('figurefirst:line2','jessyink:effectIn', 'name:appear;order:3;length:800')

layout.write_svg('jessyink_test_output.svg')

