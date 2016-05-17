#import set_params
#set_params.pdf()

from xml.dom import minidom
import matplotlib.pyplot as plt
import numpy as np

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
    """returns a float with the value xmlns:figurefirst="www.flyranch.com"of string s
    in the units of dst"""
    # need to support em, ex, px, pt, pc, cm, mm, in
    # for svg as well as percent - implemented px,in,mm and cm here
    # not sure the best way to deal with the other options
    #num,unit = upar(s)
    return in_unit[0]/scale_factors[in_unit[1]][dst_unit]

class FigureLayout(object):
    def __init__(self,layout_filename):
        """construct an object that specifies the figure layout fom the
        svg file layout_filename. Currently there are a number of restrictions
        on the format of this file.
        1) the top level svg node must contain the xmlns declaration. Also, the aspect ratio 
            of the width and height attributes must match the aspect ratio of the viewBox.
            <svg xmlns:figurefirst="www.flyranch.com"
                 width="6in"
                 height="8in"
                 viewBox="0 0 600 800"
                 ... >
        2) the layer containing the axis labels cannot have a transform attached
            it should look something like:
              <g
                 inkscape:label="Layer 1"
                 inkscape:groupmode="layer"
                 id="layer1"
                 style="display:none">
            inkscape is funny about silently adding transforms to layers
        3) the axis objects are  specified by an xml tag eg.:
            <rect
               style="fill:#0000ff;fill-rule:evenodd;stroke:none;stroke-width:10;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
               id="rect3205"
               width="33.142075"
               height="32.707672"
               x="24.71546"
               y="47.592991">
              <figurefirst:axis
                 figurefirst:name="frequency.22H05.start" /> """
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
        # dont allow sx and sy to differ
        # inkscape seems to ignore inconsistent aspect ratios by
        # only using the horizontal element of the viewbox, but 
        # it is probably best to assert that the a.r's are the same
        # for now
        assert self.layout_user_sx == self.layout_user_sy

    def from_userx(self,x,dst):
        """transfrom from user coords to dst coords"""
        x = float(x) # allow passing of strings
        #convert into layout units
        x_l = x/self.layout_user_sx[0]
        #convert from layout units into destination units
        return x_l/scale_factors[self.layout_user_sx[1]][dst]

    def from_usery(self,y,dst):
        """same as userx but for y coords,not used in this version"""
        y = float(y) # allow passing of strings
        #convert into layout units
        y_l = y/self.layout_user_sx[0]
        #convert from layout units into destination units
        return y_l/self.scale_factors[self.layout_user_sx[1]][dst]

    def make_mplfigure(self):
        """parse the xml file for elements in the figurefirst namespace of the 'axis' 
        type, return a dict with the figure and axes. Attribues of the figurefirst tag 
        are returned as a 'data' item for each axis, the aspect_ratio of the
        axis is also calculated and inserted into this item"""
        axis_elements = self.layout.getElementsByTagNameNS('www.flyranch.com','axis')
        fw_in = tounit(self.layout_width,'in')
        fh_in = tounit(self.layout_height,'in')
        fig = plt.figure(figsize=(fw_in, fh_in))
        axes = {}
        axes_groups = {'none': {}}
        for axis_element in axis_elements:
            svg_e = axis_element.parentNode
            e_x = float(svg_e.getAttribute("x"))
            e_y = float(svg_e.getAttribute("y"))
            e_w = float(svg_e.getAttribute("width"))
            e_h = float(svg_e.getAttribute("height"))
            
            # get and apply transforms
            parent_exists = True
            node = svg_e
            transforms = []
            while parent_exists:
                try:
                    transform = node.getAttribute("transform") # if there is no transform, this returns ''
                    if len(transform)>0:
                        transforms.append(transform)
                except:
                    break
                try:
                    node = node.parentNode
                    parent_exists = True
                except:
                    parent_exists = False
            if 1:
                for transform in transforms:
                    if 'matrix' in transform:
                        transform = 'np.array(' + transform.split('matrix')[1] + ')'
                        transform = eval(transform)
                        e_x = e_x*transform[0] + transform[4]
                        e_y = e_y*transform[3] + transform[5]
                        e_w = e_w*transform[0]
                        e_h = e_h*transform[3]
                
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
            
            # sort in groups
            if 'figurefirst:groupname' in axis_element.parentNode.parentNode.attributes.keys():
                group = axis_element.parentNode.parentNode.getAttribute('figurefirst:groupname')
                datadict['group'] = group
            else:
                group = 'none'
                
            axes.setdefault(name, {'axis':ax,'data':datadict})
            if group not in axes_groups.keys():
                axes_groups.setdefault(group, {})
            axes_groups[group].setdefault(name, {'axis':ax,'data':datadict})
        
        self.axes = axes
        self.axes_groups = axes_groups
        self.fig  = fig
        return {'mplfig':fig,'mplaxes':axes, 'mplaxesgrouped': axes_groups}

    def insert_mpl_in_layer(self,fflayername):
        """ takes a reference to the matplotlib figure and saves the 
        svg data into the target layer specified with the xml tag <figurefirst:targetlayer>
        this tag must have the attribute figurefirst:name = fflayername"""
        svg_string = to_svg_buffer(self.fig)
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
    
    def apply_mpl_methods(self,mplfig):
        """ apply valid mpl methods to figure"""
        for mplax in self.axes.values():
            ax = mplax['axis']
            for key, value in mplax['data'].items():
                if key.startswith('figurefirst:'):
                    potential_method = key.split('figurefirst:')[1]
                    try:
                        eval("ax."+potential_method+"("+value+")")
                        print "ax."+potential_method+"("+value+")"
                        #getattr(ax, potential_method)(eval(value))
                    except AttributeError:
                        print potential_method, 'is unknown method for mpl axes'
        

    def write_svg(self,output_filename):
        """ writes the current output_xml document to output_filename"""
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
        """ writes the current output_xml document to output_filename"""

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
        
        if 'figurefirst:groupname' in axis_element.parentNode.parentNode.attributes.keys():
            datadict['group'] = axis_element.parentNode.parentNode.getAttribute('figurefirst:groupname')
        
        ax = fig.add_axes([left, bottom, width, height])
        axes.setdefault(name, {'axis':ax,'data':datadict})

    return fig,axes,doc

def to_svg_buffer(fig):
    from StringIO import StringIO
    fid = StringIO()
    fig.savefig(fid, format='svg',transparent=True)
    fid.seek(0);
    return fid

