#import set_params
#set_params.pdf()

from xml.dom import minidom
import matplotlib.pyplot as plt

scale_factors = {'px':{'in':72.,
                    'cm':72/2.54,
                    'mm':72/25.4,
                    'px':1.},
              'in':{'in':1.,
                    'cm':0.3937,
                    'mm':0.0393,
                    'px':1/72.},
              'mm':{'in':25.4,
                    'cm':10.,
                    'mm':1,
                    'px':25.4/72},
              'cm':{'in':2.54,
                    'cm':1.,
                    'mm':0.1,
                    'px':2.54/72}}
def upar(s):
    s = str(s)
    try:
        ind=map(str.isalpha,s).index(True)
        num,unit=float(s[:ind]),s[ind:]
    except ValueError:
        num = float(s)
        unit = 'u'
    return num,unit

def tounit(s,dst):
    """returns a float with the value of string s
    in the units of dst"""
    # need to support em, ex, px, pt, pc, cm, mm, in
    # for svg as well as percent - implemented px,in,mm and cm here
    # not sure the best way to deal with the other options
    num,unit = upar(s)
    return num/scale_factors[unit][dst]

class FigureLayout(object):
    def __init__(self,layout_filename):
        self.layout_filename = layout_filename
        from xml.dom import minidom
        #layout_filename = layout_filename
        self.layout = minidom.parse(self.layout_filename).getElementsByTagName('svg')[0]
        self.layout_width = upar(self.layout.getAttribute('width'))
        self.layout_height = upar(self.layout.getAttribute('height'))
        self.layout_viewBox = self.layout.getAttribute('viewBox').split()
        self.layout_user_sx = float(self.layout_viewBox[2])/self.layout_width[0],self.layout_width[1]
        self.layout_user_sy = float(self.layout_viewBox[3])/self.layout_height[0],self.layout_height[1]
        # dont allow sx and sy to differ
        # inkscape seems to ignore inconsistent aspect ratios by
        # only using the horizontal element of the viewbox, but 
        # it is probably best to assert that the a.r's are the same
        # for now
        assert self.layout_user_sx == self.layout_user_sy

    def from_userx(self,x,dst):
        x = float(x) # allow passing of strings
        #convert into layout units
        x_l = x/self.layout_user_sx[0]
        #convert from layout units into destination units
        return x_l/scale_factors[self.layout_user_sx[1]][dst]

    def from_usery(self,y,dst):
        y = float(y) # allow passing of strings
        #convert into layout units
        y_l = y/self.layout_user_sx[0]
        #convert from layout units into destination units
        return y_l/self.scale_factors[self.layout_user_sx[1]][dst]

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
    

def read_svg_to_axes(svgfile, output_width = None):
    #72 pixels per inch
    doc = minidom.parse(svgfile)
    svgnode = doc.getElementsByTagName('svg')[0]
    width_svg_inches = tounit(svgnode.getAttribute('width'),'in')
    height_svg_inches = tounit(svgnode.getAttribute('height'),'in')
    if not(output_width is None):
        osc = output_width/width_svg_inches #output scale
    else:
        osc = 1
    fig = plt.figure(figsize=(width_svg_inches, height_svg_inches))    
    axis_elements = doc.getElementsByTagNameNS('www.flyranch.com','axis')
    axes = {}
    
    for axis_element in axis_elements:
        svg_element = axis_element.parentNode
        x_in = tounit(svg_element.getAttribute("x"),'in')
        y_in = tounit(svg_element.getAttribute("y"),'in')
        print x_in
        width_in = tounit(svg_element.getAttribute("width"),'in')
        height_in = tounit(svg_element.getAttribute("height"),'in')
        
        left = x_in/width_svg_inches
        width = width_in/width_svg_inches
        height = height_in/height_svg_inches
        bottom = (height_svg_inches-y_in-height_in)/height_svg_inches
        axis_aspect_ratio = height_in/float(width_in)
        #left = x_px/width_svg_pixels
        #width = width_px/width_svg_pixels
        #height = height_px/height_svg_pixels
        #bottom = (height_svg_pixels-y_px-height_px)/height_svg_pixels
        #axis_aspect_ratio = height_px / float(width_px)
        # a little verbose but may be a way to pass user data from the svg document to python
        datadict = {}
        [datadict.update({key:value}) for key,value in axis_element.attributes.items()]
        name = datadict.pop('figurefirst:name')
        datadict['aspect_ratio'] = axis_aspect_ratio
        
        ax = fig.add_axes([left, bottom, width, height])
        axes.setdefault(name, {'axis':ax,'data':datadict})

    return fig,axes,doc

def to_svg_buffer(fig):
    from StringIO import StringIO
    fid = StringIO()
    fig.savefig(fid, format='svg')
    fid.seek(0);
    return fid

