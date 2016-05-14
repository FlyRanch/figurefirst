#import set_params
#set_params.pdf()

from xml.dom import minidom
import matplotlib.pyplot as plt

class FigureLayout(object):
    def __init__(self,layout_filename):
        self.layout_filename = layout_filename
        self.fig,self.axes,self.layout = read_svg_to_axes(layout_filename)

    def save_svg(self,output_filename):
        self.fig,self.axes,self.layout
        indoc = self.layout.cloneNode(True)
        svg_string = to_svg_buffer(self.fig)

        from xml.dom import minidom
        mpldoc = minidom.parse(svg_string)

        # get the layers from the input dom
        layers =  indoc.getElementsByTagName('g')
        target_layer = layers[0]

        # pull out the svg parts of the xml file
        mplsvg = mpldoc.getElementsByTagName('svg')[0]
        insvg = indoc.getElementsByTagName('svg')[0]

        #need to add this namespace to the output document for some reason
        insvg.setAttribute('xmlns:xlink',mplsvg.getAttribute('xmlns:xlink'))

        #clone the child nodes in the mpl svg file into the target layer of the output dom
        mpl_svg_nodes = mplsvg.childNodes
        [target_layer.appendChild(n.cloneNode(True)) for n in mpl_svg_nodes]

        #write the modified output file
        outfile = open(output_filename,'wt')
        indoc.writexml(outfile)
        outfile.close()

def read_svg_to_axes(svgfile, px_res = 72):
    #72 pixels per inch
    doc = minidom.parse(svgfile)

    if 'in' in doc.firstChild.getAttribute('width'):
        width_inches = float(doc.firstChild.getAttribute('width').split('in')[0])
        height_inches = float(doc.firstChild.getAttribute('height').split('in')[0])
        height_svg_pixels = height_inches*px_res
        width_svg_pixels = width_inches*px_res
    else:
        width_svg_pixels = float(doc.firstChild.getAttribute('width'))
        height_svg_pixels = float(doc.firstChild.getAttribute('height'))
        print width_svg_pixels
        aspect_ratio = height_svg_pixels / float(width_svg_pixels)
        height_inches = width_inches*aspect_ratio

    fig = plt.figure(figsize=(width_inches, height_inches))

    #rects = doc.getElementsByTagName('rect')
    
    axis_elements = doc.getElementsByTagNameNS('www.flyranch.com','axis')
    
    axes = {}
    for axis_element in axis_elements:
        svg_element = axis_element.parentNode
        
        x_px = float(svg_element.getAttribute("x"))
        y_px = float(svg_element.getAttribute("y"))
        width_px = float(svg_element.getAttribute("width"))
        height_px = float(svg_element.getAttribute("height"))

        left = x_px/width_svg_pixels
        width = width_px/width_svg_pixels
        height = height_px/height_svg_pixels
        bottom = (height_svg_pixels-y_px-height_px)/height_svg_pixels
        # a little verbose but may be a way to pass user data from the svg document to python
        datadict = {}
        [datadict.update({key:value}) for key,value in axis_element.attributes.items()]
        name = datadict.pop('figurefirst:name')
        
        ax = fig.add_axes([left, bottom, width, height])
        axes.setdefault(name, {'axis':ax,'data':data})

    return fig,axes,doc

def to_svg_buffer(fig):
    from StringIO import StringIO
    fid = StringIO()
    fig.savefig(fid, format='svg')
    fid.seek(0);
    return fid

