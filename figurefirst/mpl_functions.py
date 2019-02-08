import matplotlib.pyplot as plt
import matplotlib
from matplotlib import patches
import tempfile
import shutil
import os
import sys



# Load some user parameters / defaults
# By default figurefirst will load the figurefirst_user_parameters.py file from the figurefirst/figurefirst directory.
# If you would like to set custom parameters, copy that defaults file to another location.
# Then make the changes you like and set the environment variable 'figurefirst_user_parameters' to point to the new file.
# It will be loaded instead.
try:
    figurefirst_user_parameters = os.environ['figurefirst_user_parameters']
    print('Using FigureFirst parameters loaded from: '+ figurefirst_user_parameters)
except:
    figurefirst_user_parameters = 'default'

if figurefirst_user_parameters == 'default':
    try:
        from . import figurefirst_user_parameters
    except:
        import figurefirst_user_parameters
else:
    import imp
    figurefirst_user_parameters = imp.load_source('figurefirst_user_parameters', figurefirst_user_parameters)

###################################################################################################
# Adjust Spines (Dickinson style, thanks to Andrew Straw)
###################################################################################################

# NOTE: smart_bounds is disabled (commented out) in this function. It only works in matplotlib v >1.
# to fix this issue, try manually setting your tick marks (see example below)
def adjust_spines(ax, spines, spine_locations={}, 
                  smart_bounds=True, xticks=None, yticks=None, 
                  linewidth=1, spine_location_offset=None, default_ticks=False,
                  tick_length=5,
                  color='black',
                  direction='in'):
    '''
    ax - matplotlib axis object
    spines - list of spines to include, e.g. ['left', 'bottom']
    spine_locations - dict of spine locations, e.g. {'left': 5, 'bottom': 5}. Defaults to user_parameters.
    smart_bounds - if True, stop spine at first and last ticks
    xticks - list of locations for the xticks, e.g. [0, 5, 10]
    yticks - same as xticks, for y axis
    linewidth - width of spine and tick marks
    spine_location_offset - where to place spines. Overrides spine_locations if not None.
    default_ticks - if True, skip smart bounds and tick placement. NEcessary for loglog plots to work properly. 

    '''
    if type(spines) is not list:
        spines = [spines]

    # get ticks
    if not default_ticks:
        if xticks is None:
            xticks = ax.get_xticks()
        if yticks is None:
            yticks = ax.get_yticks()

    spine_locations_dict = figurefirst_user_parameters.spine_locations
    for key in spine_locations.keys():
        spine_locations_dict[key] = spine_locations[key]
        if spine_location_offset is not None:
            spine_locations_dict[key] = spine_location_offset

    if 'none' in spines:
        #for loc, spine in ax.spines.iteritems():
        for loc, spine in ax.spines.items():
            spine.set_color('none') # don't draw spine
        ax.yaxis.set_ticks([])
        ax.xaxis.set_ticks([])
        return

    for loc, spine in ax.spines.items():
        if loc in spines:
            spine.set_position(('outward',spine_locations_dict[loc])) # outward by x points
            spine.set_linewidth(linewidth)
            spine.set_color('black')
        else:
            spine.set_color('none') # don't draw spine

    # smart bounds, if possible
    if not default_ticks:
        if int(matplotlib.__version__[0]) > 0 and smart_bounds:
            for loc, spine in ax.spines.items():
                ticks = None
                if loc in ['left', 'right']:
                    ticks = yticks
                if loc in ['top', 'bottom']:
                    ticks = xticks
                if ticks is not None and len(ticks) > 0:
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
    elif 'top' in spines:
        ax.xaxis.set_ticks_position('top')
    else:
        # no xaxis ticks
        ax.xaxis.set_ticks([])

    if not default_ticks:
        if 'left' in spines or 'right' in spines:
            ax.set_yticks(yticks)
        if 'top' in spines or 'bottom' in spines:
            ax.set_xticks(xticks)

    if default_ticks and 'left' not in spines and 'right' not in spines:
        ax.set_yticks([])
    if default_ticks and 'top' not in spines and 'bottom' not in spines:
        ax.set_xticks([])

    for line in ax.get_xticklines() + ax.get_yticklines():
        #line.set_markersize(6)
        line.set_markeredgewidth(linewidth)

    ax.tick_params(length=tick_length, color=color, direction=direction, width=linewidth)
    for spine in spines:
        ax.spines[spine].set_color(color)

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

def set_spines(layout):
    for ax in layout.axes.values():
        if 'spinespec' in ax.__dict__:
            adjust_spines(ax,[sp.strip() for sp in ax.spinespec.split(',')])

def set_fontsize(fig,fontsize):
    """
    For each text object of a figure fig, set the font size to fontsize
    fig can also be an axis object
    """
    if type(fig) != matplotlib.figure.Figure:
        fig = fig.figure # it's probably an axis, so grab the figure

    def match(artist):
        return artist.__module__ == "matplotlib.text"

    for textobj in fig.findobj(match=match):
        textobj.set_fontsize(fontsize)

def fix_mpl_svg(file_path, pattern='miterlimit:100000;', subst='miterlimit:1;'):
    """used to fix problematic outputs from the matplotlib svg
    generator, for example matplotlib creates exceptionaly large meterlimis"""
    fh, abs_path = tempfile.mkstemp()
    with open(abs_path,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    os.close(fh)

    os.remove(file_path)

    shutil.move(abs_path, file_path)
    return

def add_mpl_patch(ax, patchname, *args, **kwargs):
    """
    wrapper for these two calls:
    patch = matplotlib.patches.Patch()
    ax.add_artist(patch)
    """
    patch = getattr(patches, patchname)(*args, **kwargs)
    ax.add_artist(patch)