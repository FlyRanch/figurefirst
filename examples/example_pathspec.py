#!/usr/bin/env python
import pylab as plb # this notebook is for plotting
import numpy as np
import scipy as sp
import figurefirst as fifi

################################################
# Do an experiment and collect some data
################################################

groupA_mean = 1.5
groupA_sigma = 1.0
groupB_mean = 0.3
groupB_sigma = 0.6
c1_effect = 0.3
c2_effect = 2.0
c3_effect = 0.0
c4_effect = 0.0

data = dict()

N = 500
T = 1.
Delta = T/N
for group_name,group_mean,group_sigma in zip(['A','B'],
                                             [groupA_mean,groupB_mean],
                                             [groupA_sigma,groupB_sigma]):
    data[group_name] = dict()
    for cond_name,cond_effect in zip(['cond_1','cond_2','cond_3','cond_4'],
                                     [c1_effect,c2_effect,c3_effect,c4_effect]):
        data[group_name][cond_name] = list()
        for trial in range(10):
            W = np.zeros(N+1)
            t = np.linspace(0, T, N+1);
            W[:N+1] = cond_effect + group_mean + np.cumsum(np.sqrt(Delta) *
                                                            np.random.standard_normal(N+1) *
                                                            group_sigma)
            t = np.linspace(0, T, N+1);
            data[group_name][cond_name].append(W)

#####################################################
# Plot the data into a layout
####################################################
            
#to remove spines
def kill_spines(ax):
    return fifi.mpl_functions.adjust_spines(ax,'none', 
                  spine_locations={}, 
                  smart_bounds=True, 
                  xticks=None, 
                  yticks=None, 
                  linewidth=1)

## create a layout
layout = fifi.FigureLayout('example_pathspec_layout.svg')
## make the mpl figure objects
mplfig = layout.make_mplfigures()
## load the line and path specs to get plotting colors and effects
layout.load_pathspecs()
## iterate through what you want to plot and find the needed data,
## not the other way around..
for group_name,group in layout.axes_groups['none'].items():
    if not(group_name == 'summary'):
        #print group_name
        for cond_name,cond_ax in group.items():
            #print group_name
            group_letter = group_name.split('group')[1]
            kwargs = layout.pathspecs['trial_%s'%group_letter].mplkwargs()
            cond_ax['axis'].plot(np.array(data[group_letter][cond_name]).T,**kwargs)
            
            kill_spines(cond_ax['axis'])
            kwargs = layout.pathspecs['mean_%s'%group_letter].mplkwargs()
            cond_ax['axis'].plot(np.mean(np.array(data[group_letter][cond_name]).T,axis = 1)
                                 ,**kwargs)
            cond_ax['axis'].set_ybound(-2,5)
    else:
        group_letter = 'A'
        kwargs = layout.pathspecs['hist%s'%group_letter].mplkwargs()
        for cond_name,cond_ax in group.items():
            cond_ax['axis'].hist(np.array(data[group_letter][cond_name]).ravel(),
                                 bins = 50,histtype = 'stepfilled',clip_on = False,**kwargs)
            cond_ax['axis'].set_xbound(-2,5)
            kill_spines(cond_ax['axis'])
        group_letter = 'B'
        kwargs = layout.pathspecs['hist%s'%group_letter].mplkwargs()
        for cond_name,cond_ax in group.items():
            cond_ax['axis'].hist(np.array(data[group_letter][cond_name]).ravel(),
                                 bins =50,histtype = 'stepfilled',clip_on = False,**kwargs)
            cond_ax['axis'].set_xbound(-2,5)
            kill_spines(cond_ax['axis'])

## insert the figures into the layout and save
layout.insert_figures()
layout.set_layer_visibility('Layer 1',False)
layout.write_svg('example_pathspec_output.svg')
plb.close('all')
#display(SVG('pathspec_test_output.svg'))