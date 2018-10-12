# FigureFirst:  
FigureFirst is a python library to decorate and parse SVG files so they can serve as layout documents for matplotlib figures.
* See our github page for readme and examples: http://flyranch.github.io/figurefirst/
* Read the docs: https://figurefirst.readthedocs.io/en/latest/index.html
* Read our Scipy 2017 proceedings: http://conference.scipy.org/proceedings/scipy2017/lindsay.html

If you use FigureFirst, please cite the above paper to help others find FigureFirst.

# Use with Inkscape
FigureFirst is developed and tested with Inkscape. Some versions and settings of Inkscape are very slow. Try Inkscape 0.92: https://inkscape.org/en/release/0.92.3/

### Installing Inkscape 0.92 on Ubuntu
You can install Inkscape 0.92 using ppa:
* `sudo add-apt-repository ppa:inkscape.dev/stable`
* `sudo apt update`
* `sudo apt install inkscape`

### Optimizing Inkscape settings 
Try increasing the Rendering Tile Multiplier:
* `Edit > Preference > Rending`
* `Rendering Tile Multiplier = 50`
Restart Inkscape
