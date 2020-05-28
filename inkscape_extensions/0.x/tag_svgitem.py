#!/usr/bin/env python
import sys
sys.path.append('/usr/share/inkscape/extensions') # or another path, as necessary
sys.path.append('/Applications/Inkscape.app/Contents/Resources/extensions')
sys.path.append('C:\Program Files\Inkscape\share\extensions')
#import xml.etree.ElementTree as ET
#ET.register_namespace('figurefirst', 'http://www.figurefirst.com')

# We will use the inkex module with the predefined Effect base class.
import inkex
# The simplestyle module provides functions for style parsing.
from simplestyle import *

class FigureFirstSVGItemTagEffect(inkex.Effect):
    """
    Modified from example Inkscape effect extension. Tags object with axis tag.
    """
    def __init__(self):
        """
        Constructor.
        Defines the "--name" option of a script.
        """
        # Call the base class constructor.
        inkex.Effect.__init__(self)
        #import matplotlib
        #Define string option "--name" with "-n" shortcut and default value "World".
        self.OptionParser.add_option('-n', '--name', action = 'store',
          type = 'string', dest = 'name', default = 'none',
          help = 'Name svgitem')
        inkex.NSS[u"figurefirst"] = u"http://flyranch.github.io/figurefirst/"
        try:
            inkex.etree.register_namespace("figurefirst","http://flyranch.github.io/figurefirst/")
        except AttributeError:
            #inkex.etree._NamespaceRegistry.update(inkex.addNS("name", "figurefirst"))
            #This happens on windows version of inkscape - it might be good to check
            #and see if the namespace has been correctly added to the document
            pass

    def effect(self):
        """
        Effect behaviour.
        Overrides base class' method and inserts "Hello World" text into SVG document.
        """
        # Get script's "--what" option value.
        name = self.options.name

        # Get access to main SVG document element and get its dimensions.
        svg = self.document.getroot()
        # or alternatively
        # Create text element
        if len(self.selected.values())>1: 
            raise Exception('too many items')
        else:
            el = self.selected.values()[0]
        newElm = inkex.etree.Element(inkex.addNS("svgitem", "figurefirst"))
        newElm.attrib[inkex.addNS("name", "figurefirst")] = name
        #print inkex.NSS
        el.append(newElm)


# Create effect instance and apply it.
effect = FigureFirstSVGItemTagEffect()
effect.affect()
