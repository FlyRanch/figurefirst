#!/usr/bin/env python
import sys
sys.path.append('/usr/share/inkscape/extensions') # or another path, as necessary
sys.path.append('/Applications/Inkscape.app/Contents/Resources/extensions')
sys.path.append('C:\Program Files\Inkscape\share\extensions')
#import xml.etree.ElementTree as ET
#ET.register_namespace('figurefirst', 'http://www.figurefirst.com')

from lxml import etree

# We will use the inkex module with the predefined Effect base class.
import inkex
# The simplestyle module provides functions for style parsing.
from simplestyle import *

class FigureFirstMPLMethodsTagEffect(inkex.Effect):
    """
    Modified from example Inkscape effect extension. Tags object with mplmethods tag.
    """
    def __init__(self):
        """
        Constructor.
        Defines the "--name" option of a script.
        """
        # Call the base class constructor.
        inkex.Effect.__init__(self)
        #Define string option "--mplmethod" with "-m" shortcut and default value "none".
        self.arg_parser.add_argument('-m', '--mplmethod', 
          type = str, dest = 'mplmethod', default = 'none',
          help = 'Method name')
        #Define string option "--mplmethodarg" with "-z" shortcut and default value "none".
        self.arg_parser.add_argument('-a', '--mplmethodarg', 
          type = str, dest = 'mplmethodarg', default = 'none',
          help = 'Method arguments')
        inkex.NSS[u"figurefirst"] = u"http://flyranch.github.io/figurefirst/"
        try:
            etree.register_namespace("figurefirst","http://flyranch.github.io/figurefirst/")
        except AttributeError:
            #inkex.etree._NamespaceRegistry.update(inkex.addNS("name", "figurefirst"))
            #This happens on windows version of inkscape - it might be good to check
            #and see if the namespace has been correctly added to the document
            pass

    def effect(self):
        """
        Effect behaviour.
        Overrides base class' method and inserts figurefirst:mplmethods node into SVG document,
        with figurefirst:mplmethod, mplmethodarg attribute, value pair.
        """
        # Get script's "--what" option value.
        mplmethod = self.options.mplmethod
        mplmethodarg = self.options.mplmethodarg

        # Get access to main SVG document element and get its dimensions.
        svg = self.document.getroot()
        # or alternatively
        # Create text element
        if len(self.svg.selected.values())>1: 
            raise Exception('too many items')
        else:
            try:
                el = self.svg.selected.values()[0]
            except:
                el = list(self.svg.selected.values())[0]
        newElm = etree.Element(inkex.addNS("mplmethods", "figurefirst"))
        newElm.attrib[inkex.addNS(mplmethod, "figurefirst")] = mplmethodarg
        #print inkex.NSS
        el.append(newElm)


# Create effect instance and apply it.
effect = FigureFirstMPLMethodsTagEffect()
effect.run()
