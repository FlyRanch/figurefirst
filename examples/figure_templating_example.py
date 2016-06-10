import figurefirst

'''
To create a templated figure, draw a rectangle, and add a figurefirst:figure tag as if you were creating another figure. Then in addition to the figurefirst:name attribute, add a figurefirst:template attribute, whose value should correspond to the name of the figurefirst figure you want to use as the template. The template figure will be scaled to fill the box. 
'''

layout = figurefirst.FigureLayout('figure_templating_example.svg' )
layout.make_mplfigures()
layout.append_figure_to_layer(layout.figures['group2'], 'mpl_layer_2')
layout.append_figure_to_layer(layout.figures['group3'], 'mpl_layer_3')
layout.write_svg('figure_templating_example_output.svg')

