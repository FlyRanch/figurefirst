#import set_params
#set_params.pdf()
from xml.dom import minidom
import matplotlib.pyplot as plt
import numpy as np
XMLNS = "http://flyranch.github.io/figurefirst/"
SCALE_FACTORS = {'px':{'in':72.,
                       'cm':72/2.54,
                       'mm':72/25.4,
                       'px':1.,},
                 'in':{'in':1.,
                       'cm':0.3937,
                       'mm':0.0393,
                       'px':1/72.,},
                 'mm':{'in':25.4,
                       'cm':10.,
                       'mm':1,
                       'px':25.4/72,},
                 'cm':{'in':2.54,
                       'cm':1.,
                       'mm':0.1,
                       'px':2.54/72,}
                      }
def upar(unit_st):
    """Parse unit_st into num (float), unit (string) pair"""
    unit_st = str(unit_st)
    try:
        ind = map(str.isalpha, unit_st).index(True)
        num, unit = float(unit_st[:ind]), unit_st[ind:]
    except ValueError:
        num = float(unit_st)
        unit = 'u'
    return num, unit

def tounit(in_unit, dst_unit):
    """returns a float with the value of string s
    in the units of dst"""
    # need to support em, ex, px, pt, pc, cm, mm, in
    # for svg as well as percent - implemented px,in,mm and cm here
    # not sure the best way to deal with the other options
    #num, unit = upar(unit_st)
    return in_unit[0]/SCALE_FACTORS[in_unit[1]][dst_unit]

def get_elements_by_attr(xml_node, attribute, value):
    """helper function for xml trees when using minidom"""
    import itertools
    def recur_get_element_by_attr(xml_node, attribute, value):
        if xml_node.attributes:
            test_list = xml_node.attributes.keys()
            if attribute in test_list:
                if xml_node.getAttribute(attribute) == value:
                    yield xml_node
            nls = [recur_get_element_by_attr(nd, attribute, value) for nd in xml_node.childNodes]
            yield list(itertools.chain.from_iterable(nls))
    def flatten(container):
        #from hexparrot @ http://stackoverflow.com/questions/10823877/what-is-the-fastest-way-to-flatten-arbitrarily-nested-lists-in-python pylint: disable=redefined-builtin
        for i in container:
            if isinstance(i, (list, tuple)):
                for j in flatten(i):
                    yield j
            else:
                yield i
    return list(flatten([el for el in recur_get_element_by_attr(xml_node, attribute, value)]))

class MPLAxis(dict):
    def __getattr__(self,attr):
        return self['axis'].__getattribute__(attr)
    
class FigureLayout(object):
    def __init__(self, layout_filename, autogenlayers=True,make_mplfigures = False):
        """
        autogenlayers - if True, figurefirst will automatically create targetlayers in the svg for each figure, default: True
        make_mplfigures - if True, figurefirst will call self.make_mplfigures() during init
        
        construct an object that specifies the figure layout fom the
        svg file layout_filename. Currently there are a number of restrictions
        on the format of this file.
        1) the top level svg node must contain the xmlns declaration. Also, the aspect ratio
            of the width and height attributes must match the aspect ratio of the viewBox.
            <svg xmlns:figurefirst="http://flyranch.github.io/figurefirst/"
                 width="6in"
                 height="8in"
                 viewBox="0 0 600 800"
                 ... >
        2) the layer containing the axis labels cannot have a transform attached.
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
        self.autogenlayers = autogenlayers
        self.layout_filename = layout_filename
        #from xml.dom import minidom
        #layout_filename = layout_filename
        self.layout = minidom.parse(self.layout_filename).getElementsByTagName('svg')[0]
        self.layout_width = upar(self.layout.getAttribute('width'))
        if self.layout_width[1] == 'u':
            self.layout_width = (self.layout_width[0], 'px')
        self.layout_height = upar(self.layout.getAttribute('height'))
        if self.layout_height[1] == 'u':
            self.layout_height = (self.layout_height[0], 'px')
        self.layout_viewBox = self.layout.getAttribute('viewBox').split()
        self.layout_uw = float(self.layout_viewBox[2])
        self.layout_uh = float(self.layout_viewBox[3])
        self.layout_user_sx = self.layout_uw/self.layout_width[0], self.layout_width[1]
        self.layout_user_sy = self.layout_uh/self.layout_height[0], self.layout_height[1]
        self.output_xml = minidom.parse(self.layout_filename).cloneNode(True)
        self.axes = {}
        self.figures = {}
        self.axes_groups = {}
        # dont allow sx and sy to differ
        # inkscape seems to ignore inconsistent aspect ratios by
        # only using the horizontal element of the viewbox, but
        # it is probably best to assert that the a.r's are the same
        # for now
        assert self.layout_user_sx == self.layout_user_sy
        if make_mplfigures:
            self.make_mplfigures()

    def __getattr__(self, attr):
        if attr == 'fig':
            #from matplotlib import pyplot
            return plt.gcf()
        else:
            raise AttributeError

    def from_userx(self, x, dst):
        """transfrom from user coords to dst coords"""
        x = float(x) # allow passing of strings
        #convert into layout units
        x_l = x/self.layout_user_sx[0]
        #convert from layout units into destination units
        return x_l/SCALE_FACTORS[self.layout_user_sx[1]][dst]

    def from_usery(self, y, dst):
        """same as userx but for y coords,not used in this version"""
        y = float(y) # allow passing of strings
        #convert into layout units
        y_l = y/self.layout_user_sx[0]
        #convert from layout units into destination units
        return y_l/SCALE_FACTORS[self.layout_user_sx[1]][dst]

    def get_bounding_box_for_elements(self, axis_elements):
        left = np.inf
        right = 0
        top = np.inf
        bottom = 0
        for axis_element in axis_elements:
            e_x, e_y, e_w, e_h = self.get_xywh_for_axis_element(axis_element)
            if e_x < left:
                left = e_x
            if e_y < top:
                top = e_y
            if (e_x + e_w) > right:
                right = (e_x + e_w)
            if (e_y + e_h) > bottom:
                bottom = (e_y + e_h)
        return left, right, top, bottom
            
    def get_xywh_for_axis_element(self, axis_element, template_transform=None):
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
                transform = node.getAttribute("transform") # if no transform, this returns ''
                if len(transform) > 0:
                    transforms.append(transform)
            except:
                break
                    
            try:
                node = node.parentNode
                parent_exists = True
            except:
                parent_exists = False
        if 1:
        
        
            #el = axis_element.parentNode.getElementsByTagName('figurefirst:figure')
            #if len(el) == 1:
            #    elname = el[0].getAttribute('figurefirst:name')
            #else:
            #    elname = ''
            if template_transform is not None:# and elname == template_transform['templatename']:
                transform = np.array([ template_transform['width'], 0, 0, template_transform['height'], template_transform['x'], template_transform['y'] ] )
                transforms.append(transform)
        
            for transform in transforms:
                x_scale = 1
                y_scale = 1
                x_translation = 0
                y_translation = 0
                
                if type(transform) is unicode or type(transform) is str:
                    if 'matrix' in transform:
                        transform = 'np.array(' + transform.split('matrix')[1] + ')'
                        transform = eval(transform)
                        x_scale = transform[0]
                        y_scale = transform[3]
                        x_translation = transform[4]
                        y_translation = transform[5]
                    elif 'translate' in transform:
                        translate = transform.split('translate')[1].split(',')
                        x_translation = np.array(float(translate[0].strip('(')))
                        y_translation = np.array(float(translate[1].strip(')')))
                    elif 'scale' in transform:
                        scale = transform.split('scale')[1].split(',')
                        x_scale = float(scale[0].strip('('))
                        y_scale = float(scale[1].strip(')'))
                else:
                    x_scale = transform[0]
                    y_scale = transform[3]
                    x_translation = transform[4]
                    y_translation = transform[5]
                    
                e_x = e_x*x_scale + x_translation
                e_y = e_y*y_scale + y_translation
                e_w = e_w*x_scale
                e_h = e_h*y_scale
                
        if e_w < 0:
            e_x += e_w
            e_w *= -1
            
        if e_h < 0:
            e_y += e_h
            e_h *= -1
        
        return e_x, e_y, e_w, e_h
        
    def add_axes(self, fig, axis_elements, template_transform=None):
        """ add axes to an already constructed mpl figure, fig,
        from a collection of xml axis_element tags """
        axes_dict = dict()
        for axis_element in axis_elements:
            e_x, e_y, e_w, e_h = self.get_xywh_for_axis_element(axis_element, template_transform)

            #express things as proportion for mpl
            left = e_x/self.layout_uw
            width = e_w/self.layout_uw
            height = e_h/self.layout_uh
            bottom = (self.layout_uh-e_y-e_h)/self.layout_uh
            #Requre that each axis has a unique name. This is important so that
            #the global dict of self.axis is complete. In the case that groups
            #are used and the axis name is not unique the figurefirst:name of the
            #axis is merged with the svg_id. These unique ids are sent to figure.add_axis()
            #as the label. Perhaps it would be better to try and merge the groupname and
            #axis name before falling back to the svg id.

            ax_name = axis_element.getAttribute('figurefirst:name')
            if ax_name in self.axes.keys():
                ax_key = axis_element.parentNode.getAttribute('id') + '_' + ax_name
            else:
                ax_key = ax_name
            #print ax_key
            datadict = dict()
            [datadict.update({key:value}) for  key, value in axis_element.attributes.items()]
            projection = datadict.get('figurefirst:projection','rectilinear')
            ax = fig.add_axes([left, bottom, width, height],label = ax_key,projection = projection)
            #ax_name = datadict.pop('figurefirst:name')
            datadict['aspect_ratio'] = e_w/e_h
            mpl_methods_elements = axis_element.parentNode.getElementsByTagNameNS(XMLNS,'mplmethods')
            mpl_methods = dict()
            for mpl_methods_element in mpl_methods_elements:
                [mpl_methods.update({key:value}) for key,value in mpl_methods_element.attributes.items()]
            #add grouping
            #print axis_element.parentNode.parentNode.nodeName
            #if ('figurefirst:group' in axis_element.parentNode.parentNode.nodeName) or\
            #   ('figurefirst:figure' in axis_element.parentNode.parentNode.nodeName):
            #group = axis_element.parentNode.parentNode.getAttribute('figurefirst:name')
            #    #datadict['group'] = group
            #else:
            #    group = 'none'
            #if group not in self.axes_groups.keys():
            #    self.axes_groups.setdefault(group, {})
            #update these global dictionaries whenever an axis is added
            #self.axes_groups[group].setdefault(ax_name, {'axis':ax,'data':datadict})
            #if ax_name in self.axes.keys():
            #    ax_key = axis_element.parentNode.getAttribute('id')
            #else:
            #    ax_key = ax_name
            mplaxis = MPLAxis(axis=ax, 
                              data=datadict, 
                              name=ax_name,
                              mplmethods=mpl_methods)
            self.axes.setdefault(ax_key, mplaxis)
            axes_dict.update({ax_name:mplaxis})
            #send this one back
        return axes_dict
    
    def load_pathspecs(self):
        self.pathspecs = dict()
        elementlist = self.layout.getElementsByTagNameNS(XMLNS, 'pathspec')
        speclist = [PathSpec(el,self) for el in elementlist]
        [self.pathspecs.update({sp.name:sp}) for sp in speclist]
        
        elementlist = self.layout.getElementsByTagNameNS(XMLNS, 'linespec')
        speclist = [LineSpec(el,self) for el in elementlist]
        [self.pathspecs.update({sp.name:sp}) for sp in speclist]
        
        elementlist = self.layout.getElementsByTagNameNS(XMLNS, 'patchspec')
        speclist = [PatchSpec(el,self) for el in elementlist]
        [self.pathspecs.update({sp.name:sp}) for sp in speclist]
        
    def get_outputfile_layers(self):
        output_svg = self.output_xml.getElementsByTagName('svg')[0]
        layers = get_elements_by_attr(output_svg,"inkscape:groupmode",'layer')
        layerdict = {}
        for l in layers:
            label = attributes['inkscape:label'].value
            layerdict[label] = l
        return layerdict

    def set_layer_visability(self,inkscape_label = 'Layer 1',vis = True,gid = None,):
        import re
        value = {False:'none',True:'inline'}[vis]
        output_svg = self.output_xml.getElementsByTagName('svg')[0]
        layers = get_elements_by_attr(output_svg,"inkscape:groupmode",'layer')
        for l in layers:
            if l.attributes['inkscape:label'].value == inkscape_label:
                style_str = l.attributes['style'].value
                repl_str = re.sub(r'display:(none|inline)','display:%s'%(value),style_str)
                l.setAttribute('style',repl_str)
                
    def create_new_targetlayer(self, layer_name):
        new_layer = self.output_xml.createElement('g')
        new_targetlayer = self.output_xml.createElementNS(XMLNS, 'figurefirst:targetlayer')
        
        # check to make sure there is not already a layer with that name / id
        output_svg = self.output_xml.getElementsByTagName('svg')[0]
        layers = get_elements_by_attr(output_svg,"inkscape:groupmode",'layer')
        for layer in layers:
            if layer_name == layer.getAttribute('id') or layer_name == layer.getAttribute('inkscape:label'):
                raise ValueError( 'Layer with that name already exists!' )
        
        # set default attributes
        attributes = {u'style': u'display:inline;stroke-linecap:butt;stroke-linejoin:round', 
                      u'inkscape:label': layer_name, 
                      u'id': layer_name, 
                      u'inkscape:groupmode': 'layer',
                      }
        for attribute, value in attributes.items():
            new_layer.setAttribute(attribute, value)
        
        ff_targetlayer_name = layer_name
        new_targetlayer.setAttributeNS(XMLNS, 'figurefirst:name', ff_targetlayer_name)
        
        new_layer.appendChild(new_targetlayer)
        output_svg.appendChild(new_layer)
        
    def get_figure_element_by_name(self, name):
        figure_elements = self.layout.getElementsByTagNameNS(XMLNS, 'figure')
        figure_elements_by_name_dict = {}
        for figure_element in figure_elements:
            figname = figure_element.getAttribute('figurefirst:name')
            figure_elements_by_name_dict[figname] = figure_element
        return figure_elements_by_name_dict[name]
        
    def make_mplfigures(self):
        """parse the xml file for elements in the figurefirst namespace of the 'axis'
        type, return a dict with the figure and axes. Attribues of the figurefirst tag
        are returned as a 'data' item for each axis, the aspect_ratio of the
        axis is also calculated and inserted into this item"""

        figure_elements = self.layout.getElementsByTagNameNS(XMLNS, 'figure')
        fw_in = tounit(self.layout_width, 'in')
        fh_in = tounit(self.layout_height, 'in')
        axes_in_figures = set()
        for figure_element in figure_elements:
            fig = plt.figure(figsize=(fw_in, fh_in)) #create figure
            figname = figure_element.getAttribute('figurefirst:name')
            
            # if the figure references a template, find the template figure 
            templatename = figure_element.getAttribute('figurefirst:template')
            if len(templatename) > 0:
                template_rect = figure_element.parentNode
                figure_element = self.get_figure_element_by_name(templatename)
                axis_elements = figure_element.parentNode.getElementsByTagNameNS(XMLNS, 'axis')
                left, right, top, bottom = self.get_bounding_box_for_elements(axis_elements)
                width = right-left
                height = bottom-top
                template_transform = {  'templatename': templatename,
                                        'x': float(template_rect.getAttribute('x'))-left*(float(template_rect.getAttribute('width')) / width),
                                        'y': float(template_rect.getAttribute('y'))-top*(float(template_rect.getAttribute('height')) / height),
                                        'width': float(template_rect.getAttribute('width')) / width,
                                        'height': float(template_rect.getAttribute('height')) / height,
                                        }
            else:
                template_transform = None
            
            # get the elements within this figure grouping
            axis_elements = figure_element.parentNode.getElementsByTagNameNS(XMLNS, 'axis')
            axes_in_figures.update(set(axis_elements))
            figure_axes = self.add_axes(fig, axis_elements, template_transform=template_transform)
            self.axes_groups[figname] = figure_axes
            self.figures[figname] = fig

        all_axes = set(self.layout.getElementsByTagNameNS(XMLNS, 'axis'))
        axes_not_in_figure = all_axes.difference(axes_in_figures)
        #are we done?
        if len(axes_not_in_figure) > 0:
            #if not create a new figure
            fig = plt.figure(figsize=(fw_in, fh_in))
            self.figures['none'] = fig
            #next parse the group elements
            group_elements = self.layout.getElementsByTagNameNS(XMLNS, 'group')
            for group_element in group_elements:
                groupname = group_element.getAttribute('figurefirst:name')
                axis_elements = group_element.parentNode.getElementsByTagNameNS(XMLNS, 'axis')
                axes_in_figures.update(set(axis_elements))
                group_axes = self.add_axes(fig, axis_elements)
                #print groupname,id(group_axes)
                self.axes_groups[groupname] = group_axes
            all_axes = set(self.layout.getElementsByTagNameNS(XMLNS, 'axis'))
            axes_not_in_figure = all_axes.difference(axes_in_figures)
            #finish up
            if len(axes_not_in_figure) > 0:
                group_axes = self.add_axes(fig, list(axes_not_in_figure))
        try:
            self.fig = self.figures['none']
        except KeyError:
            pass

            #figure_axes = self.add_axes(fig,list(axes_not_in_figure))
            #group_elements = self.layout.getElementsByTagNameNS(XMLNS,'group')


            #self.axes_groups[figname] = figure_axes


            ## sort in groups
            #if 'figurefirst:groupname' in axis_element.parentNode.parentNode.attributes.keys():
            #    group = axis_element.parentNode.parentNode.getAttribute('figurefirst:groupname')
            #    datadict['group'] = group
            #else:
            #    group = 'none'


        #    if group not in axes_groups.keys():
        #        axes_groups.setdefault(group, {})
        #    axes_groups[group].setdefault(name, {'axis':ax,'data':datadict})

        #self.axes_groups = axes_groups
        #self.fig  = fig
        #return {'mplfig':fig,'mplaxes':axes, 'mplaxesgrouped': axes_groups}

    def append_figure_to_layer(self, fig, fflayername, cleartarget=False):
        svg_string = self.to_svg_buffer(fig)
        mpldoc = minidom.parse(svg_string)
        
        def get_target_layer(fflayername):
            target_layers = self.output_xml.getElementsByTagNameNS(XMLNS, 'targetlayer')
            found_target = False
            for tl in target_layers:
                if tl.getAttribute('figurefirst:name') == fflayername:
                    target_layer = tl.parentNode
                    found_target = True
                    return target_layer, found_target
            return None, found_target
        
        target_layer, found_target = get_target_layer(fflayername)
        if not(found_target):
            if self.autogenlayers:
                self.create_new_targetlayer(fflayername)
                print('Created new layer: %s'%(fflayername)) 
                target_layer, found_target = get_target_layer(fflayername)
            else:
                target_layer = target_layers[0]
                print('targetlayer %s not found inserting into %s'%(fflayername,
                                                      target_layer.getAttribute('figurefirst:name')))
                target_layer = target_layer.parentNode
        
        if cleartarget:
            try:
                self.clear_fflayer(fflayername)
            except:
                print('could not clear target, probably because desired target not found, try specifying fflayername, or use autogenlayers=True')
                
        mpl_svg = mpldoc.getElementsByTagName('svg')[0]
        output_svg = self.output_xml.getElementsByTagName('svg')[0]
        mpl_viewbox = mpl_svg.getAttribute('viewBox').split()
        output_scale = self.layout_uw/float(mpl_viewbox[2])
        mpl_svg_nodes = mpl_svg.childNodes
        [target_layer.appendChild(n.cloneNode(True)) for n in mpl_svg_nodes]
        target_layer.setAttribute('transform', 'scale(%s,%s)'%(output_scale, output_scale))
        output_svg.setAttribute('xmlns:xlink', mpl_svg.getAttribute('xmlns:xlink'))
        if fig.get_gid() is not None:
            #pass figure gid to svg
            for gr in output_svg.getElementsByTagName('g'):
                if gr.attributes:
                    if 'id' in gr.attributes.keys():
                        if gr.getAttribute('id') == "figure_1":
                            gr.setAttribute('id', fig.get_gid())
        ax_ids = [ax.get_gid() for ax in fig.get_axes() if ax.get_gid() is not None]
        if len(ax_ids) > 0:
            print 'unable to pass axes gid to svg'

    def insert_figures(self, fflayername='mpl_layer'):
        """ takes a reference to the matplotlib figure and saves the
        svg data into the target layer specified with the xml tag <figurefirst:targetlayer>
        this tag must have the attribute figurefirst:name = fflayername"""
        for fig in self.figures.values():
            self.append_figure_to_layer(fig, fflayername)

    def apply_mpl_methods(self):
        """ apply valid mpl methods to figure"""
        for mplax in self.axes.values():
            ax = mplax['axis']
            for key, value in mplax['mplmethods'].items():
                if key.startswith('figurefirst:'):
                    potential_method = key.split('figurefirst:')[1]
                    try:
                        eval("ax."+potential_method+"("+value+")")
                        #print "ax."+potential_method+"("+value+")"
                        #getattr(ax, potential_method)(eval(value))
                    except AttributeError:
                        print potential_method, 'is unknown method for mpl axes'

    def pass_xml(self, gid, key, value):
        """pass key, value pair xml pair to group with ID gid
        gid should contain prefix 'figurefirst:' to ensure uniqueness
        usage: layout.pass_xml(gid,'jessyink:effectIn', 'name:appear;order:1;length:800')"""

        if gid[:12] != 'figurefirst:':
            print """Warning: ID should start with 'figurefirst:'
                     because non-unique ids will cause silent failure in jessyink"""
        output_svg = self.output_xml.getElementsByTagName('svg')[0]
        elist = list()
        for gr in output_svg.getElementsByTagName('g'):
            if gr.attributes:
                test_list = gr.attributes.keys()
                if 'id' in test_list:
                    if gr.getAttribute('id') == gid:
                        elist.append(gr)
        if len(elist) > 1:
            print len(elist), 'groups with mataching ID found'
        elif len(elist) == 0:
            print 'ID not found'
        for el in elist:
            el.setAttribute(key, value)

    def to_svg_buffer(self, fig):
        from StringIO import StringIO
        fid = StringIO()
        fig.savefig(fid, format='svg', transparent=True)
        fid.seek(0)
        return fid

    def write_svg(self, output_filename):
        """ writes the current output_xml document to output_filename"""
        try:
            outfile = open(output_filename, 'w')
            self.output_xml.writexml(outfile, encoding='utf-8')
        except UnicodeEncodeError:
            outfile.close()
            print 'encoding error'
            outfile = open(output_filename, 'w')
            outfile.write(self.output_xml.toxml().encode('ascii', 'xmlcharrefreplace'))
            outfile.close()
            
    def save(self,filename,hidelayers = []):
        self.insert_figures()
        for l in hidelayers:
            self.set_layer_visability(l,False)
        self.write_svg(filename)

    def save_svg(self, output_filename):
        ###deprecate this function
        from xml.dom import minidom
        self.fig, self.axes, self.layout
        indoc = self.layout.cloneNode(True)
        svg_string = self.to_svg_buffer(self.fig)
        mpldoc = minidom.parse(svg_string)
        # get the layers from the input dom
        layers = indoc.getElementsByTagName('g')
        target_layer = layers[0]
        # pull out the svg parts of the xml file
        mplsvg = mpldoc.getElementsByTagName('svg')[0]
        insvg = indoc.getElementsByTagName('svg')[0]
        #need to add this namespace to the output document for some reason
        insvg.setAttribute('xmlns:xlink', mplsvg.getAttribute('xmlns:xlink'))
        #clone the child nodes in the mpl svg file into the target layer of the output dom
        mpl_svg_nodes = mplsvg.childNodes
        [target_layer.appendChild(n.cloneNode(True)) for n in mpl_svg_nodes]
        #write the modified output file
        outfile = open(output_filename, 'wt')
        indoc.writexml(outfile)
        outfile.close()

    def clear_fflayer(self, fflayername):
        '''
        If inserting mpl figure into a mpl target layer that has stuff in it,
        e.g. old mpl data, use this function to clear the layer of any children
        except the figurefirst:targetlayer node.
        '''
        target_layers = self.output_xml.getElementsByTagNameNS(XMLNS, 'targetlayer')
        for tl in target_layers:
            if tl.getAttribute('figurefirst:name') == fflayername:
                target_layer = tl.parentNode
        removed_children = 1
        while removed_children != 0: # this is not the prettiest way to do this, but it mostly works
            remove = True
            while remove: # getting a list of children and then removing them 1 by 1 does not work!
                children = target_layer.childNodes
                if len(children) == 1:
                    if children[0].nodeName == 'figurefirst:targetlayer':
                        remove = False
                    else:
                        raise ValueError('Something wrong with target layer!')

                removed_children = 0
                for child in children:
                    print child
                    if 1:
                        if child.nodeName != 'figurefirst:targetlayer':
                            print 'Removing node: ', child.nodeName
                            target_layer.removeChild(child)
                            removed_children += 1
                        else:
                            print 'Not removing: ', child.nodeName
class PathSpec(dict):
    def __init__(self,*args,**kwargs):
        for arg in args:
            try:
                if arg.tagName == 'figurefirst:pathspec':
                    self.load(arg)
                    self.name = arg.getAttributeNS("http://flyranch.github.io/figurefirst/",'name')
                if arg.tagName == 'figurefirst:linespec':
                    self.load(arg)
                    self.name = arg.getAttributeNS("http://flyranch.github.io/figurefirst/",'name')
                if arg.tagName == 'figurefirst:patchspec':
                    self.load(arg)
                    self.name = arg.getAttributeNS("http://flyranch.github.io/figurefirst/",'name')
            except AttributeError:
                if type(arg) == FigureLayout:
                    self.layout = arg
        super(PathSpec, self).__init__(**kwargs)
        
    def load(self,ptag):
        pnode = ptag.parentNode
        [self.update({k:v}) for k,v in pnode.attributes.items()]
        self.style = dict()
        [self.style.update({x.split(':')[0]:x.split(':')[1]}) for x in self['style'].split(';')]
    
class LineSpec(PathSpec):
    
    def mplkwargs(self):
        mpl_map = {'stroke':'color','stroke-opacity':'alpha','stroke-width':'lw'}
        mpl_kwargs = {}
        keylist = list()
        for k,v in self.style.items():
            try:
                mpl_kwargs[mpl_map[k]] = v
            except KeyError:
                pass
        for k,v in mpl_kwargs.items():
            if k == 'lw':
                tmp = v.split('px')[0]
                tmp = self.layout.from_userx(tmp,'in')/13.889e-3 #hard coding pnt scaling
                mpl_kwargs['lw'] = tmp
            if k == 'alpha':
                mpl_kwargs['alpha'] = float(v)
        return mpl_kwargs
    
class PatchSpec(PathSpec):
    
    def mplkwargs(self):
        mpl_map = {'stroke':'edgecolor','stroke-width':'lw','fill':'facecolor'}
        mpl_kwargs = {}
        keylist = list()
        for k,v in self.style.items():
            try:
                mpl_kwargs[mpl_map[k]] = v
            except KeyError:
                pass
        from matplotlib.colors import ColorConverter
        converter = ColorConverter()
        for k,v in mpl_kwargs.items():
            if k == 'lw':
                tmp = v.split('px')[0]
                tmp = self.layout.from_userx(tmp,'in')/13.889e-3 #hard coding pnt scaling
                mpl_kwargs['lw'] = tmp
            if k == 'edgecolor':
                mpl_kwargs['edgecolor'] = np.array(converter.to_rgba(v,float(self.style['stroke-opacity'])))
            if k == 'facecolor':
                mpl_kwargs['facecolor'] = np.array(converter.to_rgba(v,float(self.style['fill-opacity'])))
        return mpl_kwargs
    
def read_svg_to_axes(svgfile, px_res=72, width_inches=7.5):
    #72 pixels per inch
    doc = minidom.parse(svgfile)
    svgnode = doc.getElementsByTagName('svg')[0]
    if 'in' in svgnode.getAttribute('width'):
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

    axis_elements = doc.getElementsByTagNameNS(XMLNS, 'axis')

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
        [datadict.update({key:value}) for key, value in axis_element.attributes.items()]
        name = datadict.pop('figurefirst:name')
        datadict['aspect_ratio'] = axis_aspect_ratio

        if 'figurefirst:groupname' in axis_element.parentNode.parentNode.attributes.keys():
            datadict['group'] = axis_element.parentNode.parentNode.getAttribute('figurefirst:groupname')

        ax = fig.add_axes([left, bottom, width, height])
        axes.setdefault(name, {'axis':ax, 'data':datadict})

    return fig, axes, doc
