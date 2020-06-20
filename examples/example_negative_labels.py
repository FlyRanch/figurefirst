import figurefirst as fifi

layout = fifi.svg_to_axes.FigureLayout("example_negative_labels.svg")
layout.make_mplfigures()
layout.fig.set_facecolor("None")
ex = layout.axes["ex"]
ex.plot([1, 2], [3, 4])
fifi.mpl_functions.adjust_spines(ex, spines="left", yticks=[-1, -2])
layout.insert_figures("panels", cleartarget=True)
layout.write_svg("negative_labels_output.svg")
