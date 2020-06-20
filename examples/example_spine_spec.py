#!/usr/bin/env python
import figurefirst as fifi

layout = fifi.FigureLayout("example_spine_spec_layout.svg", make_mplfigures=True)
fifi.mpl_functions.set_spines(layout)
layout.save("example_spine_spec_output.svg")
