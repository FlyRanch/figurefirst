#!/usr/bin/env python
import figurefirst as fifi
import matplotlib.pyplot as plt
import matplotlib

layout = fifi.FigureLayout('example_nested_groups_layout.svg')
layout.make_mplfigures()
#print layout.axes
#layout.axes_groups['fig2']['group3']['ax2'].plot([2,3,4])
for key,ax in layout.axes.items():
	#print key
	#print type(ax)
	ax.plot([1,3,2,4])

cdict = {'r1':0.3,'r2':0.1,'r3':0.9}
for key,value in cdict.items():
    hexi = matplotlib.colors.rgb2hex(plt.cm.viridis(value))
    layout.svgitems['svggroup'][key].style['fill'] = str(hexi)

layout.apply_svg_attrs()
layout.insert_figures()
layout.write_svg('example_nested_groups_output.svg')
