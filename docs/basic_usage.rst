Basic Usage
===========

Overview
--------

With `figurefirst` creating a new figure generally involves four steps:

1.	Design the layout file. Fundamentally this means decorating a specific subset of the objects in the svg files with xml tags that identify what objects are something ```figurefirst``` should expose to Python.
2.	Convert the information in the graphical svg objects into python objects. This is accomplished via the ```figurefirst FigureLayout``` class.
3.	Plot data, taking advantage of the objects created by ```figurefirst``` to style and organize the figure.
4.	Merge newly created matplotlib figures with the original layout file and save to svg.


A multipannal figure
---------------------------

To get started it is worth examining how the figurefirst approach compares to generating a similar figure using matplotlib alone. Consider a five-panel figure with non-uniform axes sizes such as the example shown in the `matplotlib gridspec documentation <http://matplotlib.org/users/gridspec.html>`_ .

To generate this figure using only matplotlib and gridspec we would use the following code ::

	ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=3)
	ax2 = plt.subplot2grid((3, 3), (1, 0), colspan=2)
	ax3 = plt.subplot2grid((3, 3), (1, 2), rowspan=2)
	ax4 = plt.subplot2grid((3, 3), (2, 0))
	ax5 = plt.subplot2grid((3, 3), (2, 1))

.. image:: https://matplotlib.org/users/plotting/examples/demo_gridspec01.png

Now if we want to plot data to any of these axes, we can direct our plotting commands to the appropriate axes e.g. ax1.plot([1,2,3,4])

To construct a similar plot in figurefirst, we would use Inkscape to draw five boxes in an svg layout document. This layout document would specify the total dimensions of the figure (7.5 by 4.0 in) as well as the placement and aspect ratio of the axes. Then to make the figure we would construct a figurefirst:Figurelayout using the path to the layout document.

