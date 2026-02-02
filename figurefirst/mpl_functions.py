import matplotlib.pyplot as plt
import matplotlib
from matplotlib import patches
import tempfile
import shutil
import os
import sys

import matplotlib.collections as mcollections
import matplotlib.lines as mlines

# Load some user parameters / defaults
# By default figurefirst will load the figurefirst_user_parameters.py file from the figurefirst/figurefirst directory.
# If you would like to set custom parameters, copy that defaults file to another location.
# Then make the changes you like and set the environment variable 'figurefirst_user_parameters' to point to the new file.
# It will be loaded instead.
try:
    figurefirst_user_parameters = os.environ["figurefirst_user_parameters"]
    print("Using FigureFirst parameters loaded from: " + figurefirst_user_parameters)
except:
    figurefirst_user_parameters = "default"

if figurefirst_user_parameters == "default":
    try:
        from . import figurefirst_user_parameters
    except:
        import figurefirst_user_parameters
else:
    import importlib as imp

    figurefirst_user_parameters = imp.load_source(
        "figurefirst_user_parameters", figurefirst_user_parameters
    )

###################################################################################################
# Adjust Spines (Dickinson style, thanks to Andrew Straw)
###################################################################################################

# NOTE: smart_bounds is disabled (commented out) in this function. It only works in matplotlib v >1.
# to fix this issue, try manually setting your tick marks (see example below)
def adjust_spines(
    ax,
    spines,
    spine_locations={},
    smart_bounds=True,
    xticks=None,
    yticks=None,
    linewidth=1,
    spine_location_offset=None,
    default_ticks=False,
    tick_length=5,
    color="black",
    direction="in",
):
    """
    ax - matplotlib axis object
    spines - list of spines to include, e.g. ['left', 'bottom']
    spine_locations - dict of spine locations, e.g. {'left': 5, 'bottom': 5}. Defaults to user_parameters.
    smart_bounds - if True, stop spine at first and last ticks
    xticks - list of locations for the xticks, e.g. [0, 5, 10]
    yticks - same as xticks, for y axis
    linewidth - width of spine and tick marks
    spine_location_offset - where to place spines. Overrides spine_locations if not None.
    default_ticks - if True, skip smart bounds and tick placement. NEcessary for loglog plots to work properly. 

    """
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

    if "none" in spines:
        # for loc, spine in ax.spines.iteritems():
        for loc, spine in ax.spines.items():
            spine.set_color("none")  # don't draw spine
        ax.yaxis.set_ticks([])
        ax.xaxis.set_ticks([])
        return

    for loc, spine in ax.spines.items():
        if loc in spines:
            spine.set_position(
                ("outward", spine_locations_dict[loc])
            )  # outward by x points
            spine.set_linewidth(linewidth)
            spine.set_color("black")
        else:
            spine.set_color("none")  # don't draw spine

    # smart bounds, if possible
    if not default_ticks:
        if int(matplotlib.__version__[0]) > 0 and smart_bounds:
            for loc, spine in ax.spines.items():
                ticks = None
                if loc in ["left", "right"]:
                    ticks = yticks
                if loc in ["top", "bottom"]:
                    ticks = xticks
                if ticks is not None and len(ticks) > 0:
                    spine.set_bounds(ticks[0], ticks[-1])

    # turn off ticks where there is no spine
    if "left" in spines:
        ax.yaxis.set_ticks_position("left")
    elif "right" in spines:
        ax.yaxis.set_ticks_position("right")
    else:
        # no yaxis ticks
        ax.yaxis.set_ticks([])

    if "bottom" in spines:
        ax.xaxis.set_ticks_position("bottom")
    elif "top" in spines:
        ax.xaxis.set_ticks_position("top")
    else:
        # no xaxis ticks
        ax.xaxis.set_ticks([])

    if not default_ticks:
        if "left" in spines or "right" in spines:
            ax.set_yticks(yticks)
        if "top" in spines or "bottom" in spines:
            ax.set_xticks(xticks)

    if default_ticks and "left" not in spines and "right" not in spines:
        ax.set_yticks([])
    if default_ticks and "top" not in spines and "bottom" not in spines:
        ax.set_xticks([])

    for line in ax.get_xticklines() + ax.get_yticklines():
        # line.set_markersize(6)
        line.set_markeredgewidth(linewidth)

    ax.tick_params(
        length=tick_length, color=color, direction=direction, width=linewidth
    )
    for spine in spines:
        ax.spines[spine].set_color(color)


def kill_spines(ax):
    return adjust_spines(
        ax,
        "none",
        spine_locations={},
        smart_bounds=True,
        xticks=None,
        yticks=None,
        linewidth=1,
    )


def kill_labels(ax):
    # ax = ax['axis']
    for tl in ax.get_xticklabels() + ax.get_yticklabels():
        tl.set_visible(False)


def kill_all_spines(layout):
    [kill_spines(ax) for ax in layout.axes.values()]


def kill_all_labels(layout):
    [kill_labels(ax) for ax in layout.axes.values()]


def set_spines(layout):
    for ax in layout.axes.values():
        if "spinespec" in ax.__dict__:
            adjust_spines(ax, [sp.strip() for sp in ax.spinespec.split(",")])


def set_fontsize(fig, fontsize):
    """
    For each text object of a figure fig, set the font size to fontsize
    fig can also be an axis object
    """
    if type(fig) != matplotlib.figure.Figure:
        fig = fig.figure  # it's probably an axis, so grab the figure

    def match(artist):
        return artist.__module__ == "matplotlib.text"

    for textobj in fig.findobj(match=match):
        textobj.set_fontsize(fontsize)


def fix_mpl_svg(file_path, pattern="miterlimit:100000;", subst="miterlimit:1;"):
    """used to fix problematic outputs from the matplotlib svg
    generator, for example matplotlib creates exceptionaly large meterlimis"""
    fh, abs_path = tempfile.mkstemp()
    with open(abs_path, "w") as new_file:
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


#####################################################################################################
# Set zorder raster helper function -- written by Claude, tested by Floris
#####################################################################################################

def set_selective_rasterization(ax, 
                                rasterize_markers=None, 
                                rasterize_collections=None,
                                rasterize_linestyles=None,
                                raster_zorder=-1,
                                threshold=0,
                                preserve_other_zorder=True):
    """
    Selectively rasterize plot elements in a matplotlib axis.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axis object to modify
    rasterize_markers : list of str, optional
        List of marker types to rasterize (e.g., ['.', 'o', '*'])
        If None, marker type is not used as a criterion
    rasterize_collections : list of type, optional
        List of collection types to rasterize 
        (e.g., [mcollections.PathCollection, mcollections.LineCollection])
        If None, collection type is not used as a criterion
    rasterize_linestyles : list of str, optional
        List of line styles to rasterize (e.g., ['-', '--'])
        If None, linestyle is not used as a criterion
    raster_zorder : float, default=-1
        zorder value for rasterized elements (must be < threshold)
    threshold : float, default=0
        Rasterization threshold. Elements with zorder < threshold are rasterized
    preserve_other_zorder : bool, default=True
        If True, only modify zorder of elements being rasterized.
        If False, set non-rasterized elements to their original zorder (no change).
    
    Notes
    -----
    When both rasterize_markers and rasterize_linestyles are specified,
    a line will be rasterized if it matches EITHER criterion (OR logic).
    Elements not selected for rasterization are left unchanged by default.
    """
    
    # Handle collections
    for collection in ax.collections:
        should_rasterize = False
        
        if rasterize_collections is not None:
            # Check if collection type is in the rasterize list
            should_rasterize = any(isinstance(collection, ctype) 
                                  for ctype in rasterize_collections)
        
        if should_rasterize:
            collection.set_zorder(raster_zorder)
        # If preserve_other_zorder is True, don't touch non-rasterized elements
    
    # Handle line plots
    for line in ax.lines:
        should_rasterize = False
        
        marker = line.get_marker()
        linestyle = line.get_linestyle()
        
        # Check marker criteria
        marker_match = False
        if rasterize_markers is not None:
            if marker != 'None' and marker in rasterize_markers:
                marker_match = True
        
        # Check linestyle criteria  
        linestyle_match = False
        if rasterize_linestyles is not None:
            if linestyle != 'None' and linestyle in rasterize_linestyles:
                linestyle_match = True
        
        # OR logic: rasterize if EITHER condition is met
        if rasterize_markers is not None or rasterize_linestyles is not None:
            should_rasterize = marker_match or linestyle_match
        
        if should_rasterize:
            line.set_zorder(raster_zorder)
        # If preserve_other_zorder is True, don't touch non-rasterized elements
    
    # Set the rasterization threshold
    ax.set_rasterization_zorder(threshold)

def diagnose_axis_elements(ax, verbose=True):
    """
    Diagnose all plot elements in an axis that could be selectively rasterized.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axis object to diagnose
    verbose : bool, default=True
        If True, print detailed information. If False, return data structure only.
    
    Returns
    -------
    dict
        Dictionary containing information about all rasterizable elements:
        {
            'collections': list of dicts with collection info,
            'lines': list of dicts with line info,
            'summary': dict with counts by type
        }
    """
    
    diagnosis = {
        'collections': [],
        'lines': [],
        'summary': {
            'total_collections': 0,
            'total_lines': 0,
            'collection_types': {},
            'marker_types': {},
            'linestyle_types': {}
        }
    }
    
    # Analyze collections
    if verbose:
        print("=" * 70)
        print("COLLECTIONS (scatter, fill_between, etc.)")
        print("=" * 70)
    
    for i, collection in enumerate(ax.collections):
        ctype = type(collection)
        ctype_name = ctype.__name__
        
        # Get collection properties
        info = {
            'index': i,
            'type': ctype,
            'type_name': ctype_name,
            'zorder': collection.get_zorder(),
            'label': collection.get_label() if hasattr(collection, 'get_label') else None
        }
        
        # Try to get additional properties
        try:
            info['facecolor'] = collection.get_facecolor()
        except:
            pass
        
        try:
            info['edgecolor'] = collection.get_edgecolor()
        except:
            pass
        
        diagnosis['collections'].append(info)
        
        # Update summary
        diagnosis['summary']['total_collections'] += 1
        diagnosis['summary']['collection_types'][ctype_name] = \
            diagnosis['summary']['collection_types'].get(ctype_name, 0) + 1
        
        if verbose:
            print(f"\nCollection {i}:")
            print(f"  Type: {ctype_name}")
            print(f"  Full type: {ctype}")
            print(f"  Label: {info['label']}")
            print(f"  Current zorder: {info['zorder']}")
    
    # Analyze lines
    if verbose:
        print("\n" + "=" * 70)
        print("LINES (plot, with markers and linestyles)")
        print("=" * 70)
    
    for i, line in enumerate(ax.lines):
        marker = line.get_marker()
        linestyle = line.get_linestyle()
        
        info = {
            'index': i,
            'marker': marker,
            'linestyle': linestyle,
            'color': line.get_color(),
            'linewidth': line.get_linewidth(),
            'label': line.get_label(),
            'zorder': line.get_zorder()
        }
        
        diagnosis['lines'].append(info)
        
        # Update summary
        diagnosis['summary']['total_lines'] += 1
        
        if marker != 'None':
            diagnosis['summary']['marker_types'][marker] = \
                diagnosis['summary']['marker_types'].get(marker, 0) + 1
        
        if linestyle != 'None':
            diagnosis['summary']['linestyle_types'][linestyle] = \
                diagnosis['summary']['linestyle_types'].get(linestyle, 0) + 1
        
        if verbose:
            print(f"\nLine {i}:")
            print(f"  Label: {info['label']}")
            print(f"  Marker: '{marker}'")
            print(f"  Linestyle: '{linestyle}'")
            print(f"  Color: {info['color']}")
            print(f"  Linewidth: {info['linewidth']}")
            print(f"  Current zorder: {info['zorder']}")
    
    # Print summary
    if verbose:
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"\nTotal collections: {diagnosis['summary']['total_collections']}")
        if diagnosis['summary']['collection_types']:
            print("\nCollection types found:")
            for ctype, count in diagnosis['summary']['collection_types'].items():
                print(f"  {ctype}: {count}")
        
        print(f"\nTotal lines: {diagnosis['summary']['total_lines']}")
        if diagnosis['summary']['marker_types']:
            print("\nMarker types found:")
            for marker, count in diagnosis['summary']['marker_types'].items():
                print(f"  '{marker}': {count}")
        
        if diagnosis['summary']['linestyle_types']:
            print("\nLinestyle types found:")
            for linestyle, count in diagnosis['summary']['linestyle_types'].items():
                print(f"  '{linestyle}': {count}")
        
        # Provide suggestions
        print("\n" + "=" * 70)
        print("RASTERIZATION SUGGESTIONS")
        print("=" * 70)
        
        if diagnosis['summary']['collection_types']:
            print("\nTo rasterize collections, use:")
            print("  rasterize_collections=[")
            for ctype in diagnosis['summary']['collection_types'].keys():
                print(f"      mcollections.{ctype},")
            print("  ]")
        
        if diagnosis['summary']['marker_types']:
            print("\nTo rasterize by marker type, use:")
            markers = list(diagnosis['summary']['marker_types'].keys())
            print(f"  rasterize_markers={markers}")
        
        if diagnosis['summary']['linestyle_types']:
            print("\nTo rasterize by linestyle, use:")
            linestyles = list(diagnosis['summary']['linestyle_types'].keys())
            print(f"  rasterize_linestyles={linestyles}")
        
        print("\n" + "=" * 70)
    
    return diagnosis