import numpy as np
import matplotlib.pyplot as plt
import figurefirst

'''
This example contains 3 methods for creating the same output from the same layout file. 
Choose the method most appropriate to your use-case as a starting template.

Method 1: Basic, linear code
Method 2: Make the 2 figures independently - this is what you would do if using two seperate scripts to make your final figure output
Method 3: More sophisticated code, using loops to address the nested group structure

To run all examples, see bottom of file starting with " if __name__ == '__main__' "
'''

def get_example_x_and_y_data():
    x = np.linspace(0,10,100)
    possible_y_outputs = [np.sin(x)*np.random.random(), 
                          np.exp(x),
                          x**2,
                          np.sqrt(x)]
    y = possible_y_outputs[ np.random.choice(range(len(possible_y_outputs))) ]
    return x, y

def method_1():
    # Create layout object from layout svg file
    layout = figurefirst.svg_to_axes.FigureLayout('example_minimal_multi_fig_multi_ax_template_layout.svg', make_mplfigures=True)
    
    # Figure 1, axis a
    x, y = get_example_x_and_y_data()
    ax = layout.axes[('figure1', 'axis_a')]
    ax.plot(x,y,color='blue')
    figurefirst.mpl_functions.adjust_spines(ax, ['left'])

    # copy data over to figure 1 copy, axis a
    ax = layout.axes[('figure1_copy', 'axis_a')]
    ax.plot(x,y,color='blue')
    figurefirst.mpl_functions.adjust_spines(ax, ['left'])

    # Figure 1, axis b
    x, y = get_example_x_and_y_data()
    ax = layout.axes[('figure1', 'axis_b')]
    ax.plot(x,y,color='green')
    figurefirst.mpl_functions.adjust_spines(ax, ['left', 'bottom'])
    
    # Figure 2, axis a
    # axis tag names in different figures can be identical, and still create unique axis objects
    x, y = get_example_x_and_y_data()
    ax = layout.axes[('figure2', 'axis_a')]
    ax.plot(x,y,color='black')
    figurefirst.mpl_functions.adjust_spines(ax, [])
    
    # Figure 2, axis d
    # axis tag names in different figures can can also be different
    x, y = get_example_x_and_y_data()
    ax = layout.axes[('figure2', 'axis_d')]
    ax.plot(x,y,color='blue')
    figurefirst.mpl_functions.adjust_spines(ax, ['right', 'bottom'])
    
    # Set axis fontsize
    figurefirst.mpl_functions.set_fontsize(layout.figures['figure1'], 8)
    figurefirst.mpl_functions.set_fontsize(layout.figures['figure2'], 8)

    # Render figure 1 and 2
    layout.append_figure_to_layer(layout.figures['figure1'], 'figure1', cleartarget=True)
    layout.append_figure_to_layer(layout.figures['figure2'], 'figure2', cleartarget=True)
    layout.append_figure_to_layer(layout.figures['figure1_copy'], 'figure1_copy', cleartarget=True)

    # Write (save) the resulting svg
    layout.write_svg('output_of_examples/example_minimal_multi_fig_multi_ax_template_layout.svg')
    
if __name__ == '__main__':
    
    # Basic, linear code
    method_1()
    
        
        
        
        
        
        
        
        
        
