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

def tounit(in_unit,dst_unit):
    """returns a float with the value of string s
    in the units of dst"""
    # need to support em, ex, px, pt, pc, cm, mm, in
    # for svg as well as percent - implemented px,in,mm and cm here
    # not sure the best way to deal with the other options
    #num,unit = upar(s)
    return in_unit[0]/scale_factors[in_unit[1]][dst_unit]

class FigureLayout(object):
    def __init__(self,layout_filename):
        self.layout_filename = layout_filename
        from xml.dom import minidom
        #layout_filename = layout_filename
        self.layout = minidom.parse(self.layout_filename).getElementsByTagName('svg')[0]
        self.layout_width = upar(self.layout.getAttribute('width'))
        self.layout_height = upar(self.layout.getAttribute('height'))
        self.layout_viewBox = self.layout.getAttribute('viewBox').split()
        self.layout_uw = float(self.layout_viewBox[2])
        self.layout_uh = float(self.layout_viewBox[3])
        self.layout_user_sx = self.layout_uw/self.layout_width[0],self.layout_width[1]
        self.layout_user_sy = self.layout_uh/self.layout_height[0],self.layout_height[1]
        self.output_xml = minidom.parse(self.layout_filename).cloneNode(True)
        self.loaded = dict()
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

    def make_mplfigure(self):
        axis_elements = self.layout.getElementsByTagNameNS('www.flyranch.com','axis')
        fw_in = tounit(self.layout_width,'in')
        fh_in = tounit(self.layout_height,'in')
        fig = plt.figure(figsize=(fw_in, fh_in))
        axes = {}
        for axis_element in axis_elements:
            svg_e = axis_element.parentNode
            e_x = float(svg_e.getAttribute("x"))
            e_y = float(svg_e.getAttribute("y"))
            e_w = float(svg_e.getAttribute("width"))
            e_h = float(svg_e.getAttribute("height"))
            #express things as proportion for mpl
            left = e_x/self.layout_uw
            width = e_w/self.layout_uw
            height = e_h/self.layout_uh
            bottom = (self.layout_uh-e_y-e_h)/self.layout_uh
            ax = fig.add_axes([left, bottom, width, height])
            datadict = {}
            [datadict.update({key:value}) for key,value in axis_element.attributes.items()]
            name = datadict.pop('figurefirst:name')
            datadict['aspect_ratio'] = e_w/e_h
            axes.setdefault(name, {'axis':ax,'data':datadict})
        self.loaded.update({'mplfig':fig,'mplaxes':axes})
        return {'mplfig':fig,'mplaxes':axes}

    def insert_mpl_in_layer(self,mplfig,fflayername):
        svg_string = to_svg_buffer(mplfig['mplfig'])
        mpldoc = minidom.parse(svg_string)
        target_layers = self.output_xml.getElementsByTagNameNS('www.flyranch.com','targetlayer')
        for tl in target_layers:
            print tl.getAttribute('figurefirst:name')
            if tl.getAttribute('figurefirst:name') == fflayername:
                target_layer = tl.parentNode
        mpl_svg = mpldoc.getElementsByTagName('svg')[0]
        output_svg = self.output_xml.getElementsByTagName('svg')[0]    
        mpl_viewbox = mpl_svg.getAttribute('viewBox').split()
        output_scale = self.layout_uw/float(mpl_viewbox[2])
        mpl_svg_nodes = mpl_svg.childNodes
        [target_layer.appendChild(n.cloneNode(True)) for n in mpl_svg_nodes]
        target_layer.setAttribute('transform','scale(%s,%s)'%(output_scale,output_scale))
        output_svg.setAttribute('xmlns:xlink',mpl_svg.getAttribute('xmlns:xlink'))
        
    def write_svg(self,output_filename):
        outfile = open(output_filename,'wt')
        self.output_xml.writexml(outfile)
        outfile.close()
        
    def save_svg(self,output_filename):
        ###depreciate this function
        from xml.dom import minidom
        self.fig,self.axes,self.layout
        indoc = self.layout.cloneNode(True)
        svg_string = to_svg_buffer(self.fig)
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
        

def read_svg_to_axes(svgfile, px_res = 72, width_inches = 7.5):
    #72 pixels per inch
    doc = minidom.parse(svgfile)
    svgnode = doc.getElementsByTagName('svg')[0]
    if 'in' in svgnode.getAttribute('width'):
        print 'here'
        width_inches = float(svgnode.getAttribute('width').split('in')[0])
        height_inches = float(svgnode.getAttribute('height').split('in')[0])
        height_svg_pixels = height_inches*px_res
        width_svg_pixels = width_inches*px_res
    else:
        width_svg_pixels = float(svgnode.getAttribute('width'))
        height_svg_pixels = float(svgnode.getAttribute('height'))
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
        axis_aspect_ratio = height_px / float(width_px)
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
    fig.savefig(fid, format='svg',transparent=True)
    fid.seek(0);
    return fid

