from figurefirst import FigureLayout
layout = FigureLayout('f2_layout.svg')

mplfig = layout.make_mplfigure()
import numpy as np
mplfig['mplfig'].patch.set_facecolor('None')
for mplax in mplfig['mplaxes'].values():
    ax = mplax['axis']
    ax.plot(np.arange(30),np.random.rand(30)*300,color = 'k')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.patch.set_facecolor('None')
layout.apply_mpl_methods(mplfig)
layout.insert_mpl_in_layer(mplfig,'mpl_panel_a')
layout.write_svg('test_output.svg')

