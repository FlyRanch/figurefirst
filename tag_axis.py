#!/usr/bin/env python
import sys
sys.path.append('/usr/share/inkscape/extensions') # or another path, as necessary
sys.path.append('/Applications/Inkscape.app/Contents/Resources/extensions')
#import xml.etree.ElementTree as ET
#ET.register_namespace('figurefirst', 'http://www.figurefirst.com')

# We will use the inkex module with the predefined Effect base class.
import inkex
# The simplestyle module provides functions for style parsing.
from simplestyle import *

class FigureFirstAxisTagEffect(inkex.Effect):
    """
    Modified from example Inkscape effect extension. Tags object with axis tag.
    """
    def __init__(self):
        """
        Constructor.
        Defines the "--what" option of a script.
        """
        # Call the base class constructor.
        inkex.Effect.__init__(self)

        # Define string option "--what" with "-w" shortcut and default value "World".
        self.OptionParser.add_option('-n', '--name', action = 'store',
          type = 'string', dest = 'name', default = 'none',
          help = 'Name axis')
        inkex.NSS[u"figurefirst"] = u"http://flyranch.github.io/figurefirst/"
        inkex.etree.register_namespace("figurefirst","http://flyranch.github.io/figurefirst/")
        #ET.register_namespace('figurefirst', "http://flyranch.github.io/figurefirst/")


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
        # svg = self.document.xpath('//svg:svg',namespaces=inkex.NSS)[0]

        # Again, there are two ways to get the attibutes:
        width  = self.unittouu(svg.get('width'))
        height = self.unittouu(svg.attrib['height'])
        # Create text element
        el = self.selected.items()[0][1]
        newElm = inkex.etree.Element(inkex.addNS("axis", "figurefirst"))
        newElm.attrib[inkex.addNS("name", "figurefirst")] = name
        #print inkex.NSS
        el.append(newElm)


# Create effect instance and apply it.
effect = FigureFirstAxisTagEffect()
effect.affect()