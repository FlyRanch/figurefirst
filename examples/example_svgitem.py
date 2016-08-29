import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import figurefirst as fifi 

layout = fifi.FigureLayout('example_svgitem_layout.svg')
layout.make_mplfigures()
cdict1 = {'r1':0.3,'r2':0.1,'r3':0.9}
cdict2 = {'path1':0.3,'path2':0.1,'path3':0.9}
for key,patch in layout.svgitems['svggroup'].items():
    clev = cdict1[key]
    hexi = matplotlib.colors.rgb2hex(plt.cm.viridis(clev))
    patch.style['fill'] = str(hexi)

for key,patch in layout.svgitems['pathgroup'].items():
    clev = cdict2[key]
    hexi = matplotlib.colors.rgb2hex(plt.cm.viridis(clev))
    patch.style['fill'] = str(hexi)
    
layout.svgitems['l1'].style['fill'] = str(hexi)
layout.svgitems['l1'].text = str(clev)

layout.apply_svg_attrs()
layout.save('example_svgitem_output.svg')