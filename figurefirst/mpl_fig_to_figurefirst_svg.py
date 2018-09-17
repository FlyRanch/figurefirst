from xml.dom import minidom
from . svg_to_axes import FigureLayout, repar, tounit, XMLNS, get_elements_by_attr
import copy

import matplotlib.pyplot as plt
import numpy as np

import pkg_resources

def get_empty_svg_document(tmp_filename='.fifi_tmp.svg'):
    '''
    Creates basic svg template file and saves it to disk. Returns the filename.
    '''
    doc = minidom.Document()
    svg = doc.createElement('svg')

    attributes = {'xmlns:figurefirst': "http://flyranch.github.io/figurefirst/",
                    'xmlns:dc': "http://purl.org/dc/elements/1.1/",
                    'xmlns:cc': "http://creativecommons.org/ns#",
                    'xmlns:rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                    'xmlns:svg': "http://www.w3.org/2000/svg",
                    'xmlns': "http://www.w3.org/2000/svg",
                    'xmlns:inkscape': "http://www.inkscape.org/namespaces/inkscape",
                    'width': "6in",
                    'height': "3in",
                    'viewBox': "0 0 432 216",
                    'id': "svg2",
                    'version': "1.1",
                    'inkscape:version': "0.91 r13725",
                   }

    for attribute, value in attributes.items():
        svg.setAttribute(attribute, value)

    doc.appendChild(svg)
    outfile = open(tmp_filename, 'w')
    doc.writexml(outfile, encoding='utf-8')

    return tmp_filename

def set_figure_size(fig, layout):
    svg = layout.output_xml.getElementsByTagName('svg')[0]

    width, height = fig.get_size_inches()
    svg.setAttribute('width', repar(width, 'in'))
    svg.setAttribute('height', repar(height, 'in'))
    viewBox = "0 0 " + str(width*72) + " " + str(height*72)
    svg.setAttribute('viewBox', viewBox)
    
    return layout

def load_template_svg():
    tmp_filename = get_empty_svg_document()
    return FigureLayout(tmp_filename)

def create_rect_for_ax(layout, parent, ax, name):
    new_rect = layout.output_xml.createElement('rect')
    figurefirst_axis_tag = layout.output_xml.createElementNS(XMLNS, 'figurefirst:axis')
    figurefirst_axis_tag.setAttribute("figurefirst:name", name)

    bbox = ax.get_position() 
    width, height = ax.figure.get_size_inches()

    # set default attributes
    attributes = {  u'x': unicode(width*tounit([bbox.x0,'in'],'px')),
                    u'y': unicode(height*tounit([1-bbox.y0-bbox.height,'in'],'px')),
                    u'width': unicode(width*tounit([bbox.width,'in'],'px')),
                  	u'height': unicode(height*tounit([bbox.height,'in'],'px')),
                  }

    for attribute, value in attributes.items():
        new_rect.setAttribute(attribute, value)

    new_rect.appendChild(figurefirst_axis_tag)
    parent.appendChild(new_rect)

def mpl_fig_to_figurefirst_svg(mpl_fig, output_filename, design_layer_name='mpl_design_layer', figurefirst_figure_name='mpl_output_layer'):
    '''
    Given a matplotlib figure (mpl_fig) with multiple axes, this function creates an
    svg file (output_filename) that conforms to the figurefirst specs with rectangles
    drawn and tagged for each matplotlib axis. The axes are grouped together under a
    figurefirst:figure tag (name:mpl_output_layer), and the layout is saved to svg. 
    '''
    layout = load_template_svg()
    layout = set_figure_size(mpl_fig, layout)

    layout.create_new_targetlayer(design_layer_name)

    output_svg = layout.output_xml.getElementsByTagName('svg')[0]
    layer = get_elements_by_attr(output_svg,"inkscape:label", design_layer_name)[0]

    group = layout.output_xml.createElement('g')
    layer.appendChild(group)

    figurefirst_figure_tag = layout.output_xml.createElementNS(XMLNS, 'figurefirst:figure')
    figurefirst_figure_tag.setAttribute("figurefirst:name", figurefirst_figure_name)

    group.appendChild(figurefirst_figure_tag)

    for i, ax in enumerate(mpl_fig.axes):
        create_rect_for_ax(layout, group, ax, 'ax'+str(i))

    layout.write_svg(output_filename)
    layout = FigureLayout(output_filename, make_mplfigures=True)

    return layout

def add_mpl_fig_to_figurefirst_svg(fifi_svg_filename, mpl_fig, output_filename, design_layer_name='mpl_design_layer', figurefirst_figure_name='mpl_template'):
    layout = FigureLayout(fifi_svg_filename)

    layout.create_new_targetlayer(design_layer_name)

    output_svg = layout.output_xml.getElementsByTagName('svg')[0]
    layer = get_elements_by_attr(output_svg,"inkscape:label", design_layer_name)[0]

    group = layout.output_xml.createElement('g')
    layer.appendChild(group)

    figurefirst_figure_tag = layout.output_xml.createElementNS(XMLNS, 'figurefirst:figure')
    figurefirst_figure_tag.setAttribute("figurefirst:name", figurefirst_figure_name)

    group.appendChild(figurefirst_figure_tag)

    for i, ax in enumerate(mpl_fig.axes):
       create_rect_for_ax(layout, group, ax, 'ax'+str(i))

    layout.write_svg(output_filename)
    layout = FigureLayout(output_filename, make_mplfigures=True)

    return layout
