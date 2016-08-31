import matplotlib.pyplot as plt
import matplotlib


###################################################################################################
# Adjust Spines (Dickinson style, thanks to Andrew Straw)
###################################################################################################

# NOTE: smart_bounds is disabled (commented out) in this function. It only works in matplotlib v >1.
# to fix this issue, try manually setting your tick marks (see example below) 
def adjust_spines(ax,spines, spine_locations={}, smart_bounds=True, xticks=None, yticks=None, linewidth=1):
    if type(spines) is not list:
        spines = [spines]
        
    # get ticks
    if xticks is None:
        xticks = ax.get_xticks()
    if yticks is None:
        yticks = ax.get_yticks()
        
    spine_locations_dict = {'top': 10, 'right': 10, 'left': 10, 'bottom': 10}
    for key in spine_locations.keys():
        spine_locations_dict[key] = spine_locations[key]
        
    if 'none' in spines:
        for loc, spine in ax.spines.iteritems():
            spine.set_color('none') # don't draw spine
        ax.yaxis.set_ticks([])
        ax.xaxis.set_ticks([])
        return
    
    for loc, spine in ax.spines.iteritems():
        if loc in spines:
            spine.set_position(('outward',spine_locations_dict[loc])) # outward by x points
            spine.set_linewidth(linewidth)
            spine.set_color('black')
        else:
            spine.set_color('none') # don't draw spine
            
    # smart bounds, if possible
    if int(matplotlib.__version__[0]) > 0 and smart_bounds: 
        for loc, spine in ax.spines.items():
            if loc in ['left', 'right']:
                ticks = yticks
            if loc in ['top', 'bottom']:
                ticks = xticks
            spine.set_bounds(ticks[0], ticks[-1])

    # turn off ticks where there is no spine
    if 'left' in spines:
        ax.yaxis.set_ticks_position('left')
    elif 'right' in spines:
        ax.yaxis.set_ticks_position('right')
    else:
        # no yaxis ticks
        ax.yaxis.set_ticks([])

    if 'bottom' in spines:
        ax.xaxis.set_ticks_position('bottom')
    if 'top' in spines:
        ax.xaxis.set_ticks_position('top')
    else:
        # no xaxis ticks
        ax.xaxis.set_ticks([])    
    
    if 'left' in spines or 'right' in spines:
        ax.set_yticks(yticks)
    if 'top' in spines or 'bottom' in spines:
        ax.set_xticks(xticks)
    
    for line in ax.get_xticklines() + ax.get_yticklines():
        #line.set_markersize(6)
        line.set_markeredgewidth(linewidth)

        
def kill_spines(ax):
    return adjust_spines(ax,'none', 
                  spine_locations={}, 
                  smart_bounds=True, 
                  xticks=None, 
                  yticks=None, 
                  linewidth=1)

def kill_labels(ax):
    #ax = ax['axis']
    for tl in ax.get_xticklabels() + ax.get_yticklabels():
            tl.set_visible(False)

def kill_all_spines(layout):
    [kill_spines(ax) for ax in layout.axes.values()]

def kill_all_labels(layout):
    [kill_labels(ax) for ax in layout.axes.values()]