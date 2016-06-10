import figurefirst

layout = figurefirst.FigureLayout('figure_templating_example.svg' )
layout.make_mplfigures()
layout.append_figure_to_layer(layout.figures.values()[2], 'mpl_layer_2')
layout.append_figure_to_layer(layout.figures.values()[3], 'mpl_layer_3')
layout.append_figure_to_layer(layout.figures.values()[4], 'mpl_layer_4')
layout.write_svg('figure_templating_example_output.svg')

