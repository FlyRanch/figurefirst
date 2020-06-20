import figurefirst
import numpy as np

"""
To create a templated figure, draw a rectangle, and add a figurefirst:figure tag as if you were creating another figure. Then in addition to the figurefirst:name attribute, add a figurefirst:template attribute, whose value should correspond to the name of the figurefirst figure you want to use as the template. The template figure will be scaled to fill the box. 
"""

# manually create layers


def populate_axes_with_data(ax, color):
    ax.plot(np.random.random(100), np.random.random(100), "o", color=color)


layout = figurefirst.FigureLayout(
    "multi_figures_autogen_targetlayers.svg", autogenlayers=False
)

layout.make_mplfigures()

name_to_color = {
    "figure1": "blue",
    "figure2": "red",
}

for figure_name, group in layout.axes_groups.items():
    for axis_name, axis in group.items():
        populate_axes_with_data(axis, name_to_color[figure_name])

layout.create_new_targetlayer("figure1")
layout.create_new_targetlayer("figure2")

layout.append_figure_to_layer(layout.figures["figure1"], "figure1")
layout.append_figure_to_layer(layout.figures["figure2"], "figure2")

layout.set_layer_visibility("Design_layer", False)

layout.write_svg("multi_figures_autogen_targetlayers_manual.svg")


# auto gen layers based on need


def populate_axes_with_data(ax, color):
    ax.plot(np.random.random(100), np.random.random(100), "o", color=color)


layout = figurefirst.FigureLayout(
    "multi_figures_autogen_targetlayers.svg", autogenlayers=True
)

layout.make_mplfigures()

name_to_color = {
    "figure1": "blue",
    "figure2": "red",
}

for figure_name, group in layout.axes_groups.items():
    for axis_name, axis in group.items():
        populate_axes_with_data(axis, name_to_color[figure_name])

layout.append_figure_to_layer(layout.figures["figure1"], "figure1")
layout.append_figure_to_layer(layout.figures["figure2"], "figure2")

layout.set_layer_visibility("Design_layer", False)

layout.write_svg("multi_figures_autogen_targetlayers_auto.svg")
