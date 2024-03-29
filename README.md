# FigureFirst
FigureFirst is a python 3.5+ library to decorate and parse SVG files so they can serve as layout documents for matplotlib figures. In principle FigureFirst works on python 2.7, but it is not officially supported. 
* See our github page for readme and examples: http://flyranch.github.io/figurefirst/
* Read the docs: https://figurefirst.readthedocs.io/en/latest/index.html
* Read our Scipy 2017 proceedings: http://conference.scipy.org/proceedings/scipy2017/lindsay.html

If you use FigureFirst, please cite the above paper to help others find FigureFirst.

## Installation

#### Install `figurefirst` using pip

```bash
pip install figurefirst
```
#### Installing `figurefirst` inkscape extensions

This package includes a console script, `figurefirst_ext` to install inkscape extensions.
It tries to infer the default installation path for your OS (do `figurefirst_ext --help` to see what they are),
or you can pass a path in manually, e.g..

```bash
figurefirst_ext ~/.config/inkscape/extensions
```

This defaults to installing extensions for inkscape 1.0. If need support for older version of Inkscape (<1.0) add `--inkscape_major_version 0` to the above command. 

## Quickstart
*See http://flyranch.github.io/figurefirst/ for more detail, or follow the tutorial notebook: https://github.com/FlyRanch/figurefirst/blob/master/examples/tutorial/tutorial.ipynb*
1. Create your figure template in Inkscape. 
    *  Make a rectangle for each panel, tag the panel using `extensions > figurefirst > tagaxis`, e.g. `A` or `B`
    *  Group the rectangles (select all, `ctrl-g`), tag the group using `extensions > figurefirst > tagfigure`, e.g. `fig1`
    *  Save your template, e.g. `fifi_template.svg`
2. In Python use the following commands to load, plot, and save:
    *  `import figurefirst as fifi`
    *  `layout = fifi.svg_to_axes.FigureLayout('fifi_template.svg', autogenlayers=True, make_mplfigures=True, hide_layers=[])`
    *  For each axis, grab the axis handle using: `ax = layout.axes[('fig1', 'B')]`
    *  Plot on that axis using matplotlib as usual
    *  After you have plotted all panels, optionally update the aesthetics:
        *  `fifi.mpl_functions.adjust_spines(ax, ['left', 'bottom'])`
        *  `fifi.mpl_functions.set_fontsize(ax, 6)`
    *  Add your figure to the layout using `layout.append_figure_to_layer(layout.figures['fig1'], 'fig1', cleartarget=True)`
    *  Save your figure to the svg using `layout.write_svg('fifi_template.svg')`. Use a new name if you wish not to overwrite the template. 
3. Note that you can have multiple figurefirst "figures" in a single svg file. Each figure will appear as a new layer.  
4. If working in a jupyter notebook, you can display the figure using
    *  `from IPython.display import display,SVG`
    *  `display(SVG('fifi_template.svg'))`
5. If wanting to export to PDF:
    *  `import cairosvg`
    *  `cairosvg.svg2pdf(url='fifi_template.svg', write_to='fifi_template.pdf')`

## Quickstart Video Tutorial
[![FigureFirst Quickstart Tutorial](http://img.youtube.com/vi/wG5R0EMcBuI/0.jpg)](http://www.youtube.com/watch?v=wG5R0EMcBuI "FigureFirst Quickstart Tutorial")

## Use with Inkscape
FigureFirst is developed and tested with Inkscape. Some versions and settings of Inkscape are very slow, try using inkcsape 1.0. For legacy versions of Inkscape specifying the Inkscape major version as 0 in the install script. See [installation](#installation) above.

You may find issues with with plugins for Inkscape > 1.0. You can install Inkscape 1.0 via the following link: [Inkscape 1.0](https://inkscape.org/release/inkscape-1.0/)

We welcome pull requests to fix compatibility with more recent version of Inkscape!

#### Optimizing Inkscape settings
Try increasing the Rendering Tile Multiplier:
* `Edit > Preference > Rending`
* `Rendering Tile Multiplier = 50`
Restart Inkscape

## Development

- Clone this repo
- Test locally by running `pytest`
  - To keep the test output files for inspection, add the `--keep_files` option
  - To test against all supported python versions, run `tox`
- We use [black](https://pypi.org/project/black/) for code formatting. 
- Enable your github account with travis for continuous integration
- Raise a pull request


## FAQ
* How can I control the order of axes that are overlapping? To put axis 'a' on top of axis 'b', when both are in the same group 'fig':
  *  `layout = fifi.svg_to_axes.FigureLayout('fifi_axis_order.svg', autogenlayers=True, make_mplfigures=False)`
  *  `layout.make_mplfigures(axes_order={'fig': ['a', 'b']})`
  
* After plotting, inkscape is very slow (because there are lots of points/lines). Rasterize using `ax.set_rasterization_zorder(ZORDER)` see https://matplotlib.org/3.1.3/gallery/misc/rasterization_demo.html
