import os
from xml.dom import minidom
import matplotlib.pyplot as plt
import numpy as np
from warnings import warn
import traceback
import time
import sys
import copy

if (sys.version_info > (3, 0)):
    PY3 = True
else:
    PY3 = False

# Load some user parameters / defaults
# By default figurefirst will load the figurefirst_user_parameters.py file from the figurefirst/figurefirst directory.
# If you would like to set custom parameters, copy that defaults file to another location.
# Then make the changes you like and set the environment variable 'figurefirst_user_parameters' to point to the new file.
# It will be loaded instead.
import os
try:
    figurefirst_user_parameters = os.environ['figurefirst_user_parameters']
    print('Using FigureFirst parameters loaded from: '+ figurefirst_user_parameters)
except:
    figurefirst_user_parameters = 'default'

if figurefirst_user_parameters == 'default':
    try:
        from . import figurefirst_user_parameters
    except:
        import figurefirst_user_parameters
else:
    import imp
    figurefirst_user_parameters = imp.load_source('figurefirst_user_parameters', figurefirst_user_parameters)


if PY3:
    try:
        from . import regenerate
    except:
        import regenerate

try:
    from . import mpl_functions
except:
    import mpl_functions

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
        #Python 3 mod
        ind = list(map(str.isalpha, unit_st)).index(True)

        num, unit = float(unit_st[:ind]), unit_st[ind:]
    except ValueError:
        num = float(unit_st)
        unit = 'u'
    return num, unit

def repar(val, unit):
    """reparse a value and unit into a string for writing into an svg"""
    if unit not in SCALE_FACTORS.keys():
        raise ValueError("Unit not recognized, use px, in, mm, or cm")
    return str(val) + unit

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

def flatten_list(container):
    for i in container:
        if isinstance(i, (list)):
            for j in flatten_list(i):
                yield j
        else:
            yield i
    #from hexparrot @ http://stackoverflow.com/questions/10823877/
    #what-is-the-fastest-way-to-flatten-arbitrarily-nested-lists-in-python

def flatten_dict(d):
    """unrap a nested dict, d, returns a new dictionary with that have tuples
    as keys that specify the path through the original dictionary tree to the
    leaf. e.g. {'l1key': {'l2key1':item1,'l2key2':item2}} will become
    {('l1key','l2key1'):item1,('l1key','l2key2'):item2}"""
    import copy
    keylist = []
    def traverse(kl,d):
        if len(d) == 0:
            yield {tuple(kl):d}
        else:
            for key,value in d.items():
                new_keylist = copy.copy(kl)
                new_keylist.append(key)
                yield [l for l in traverse(new_keylist,value)]
    flat_dict = {}
    fd_list = [fd for fd in flatten_list(list(traverse(keylist,d)))]
    [flat_dict.update(fd) for fd in flatten_list(list(traverse(keylist,d)))]
    return flat_dict

def extractTreeByType(node, searchType):
    """walk a nested dictionary and pop the items of a
    certain type from the dictionary"""
    temp = dict()
    for key, value in node.items():
        if isinstance(value,searchType):
            temp.update({key:value})
        elif isinstance(value,dict):
            rval = extractTreeByType(value,searchType)
            if len(rval.keys()) > 0:
                temp.update({key:rval})
    return temp

def filterTreeByType(node, searchType):
    for key, value in node.items():
        if isinstance(value,searchType):
            node.pop(key)
        else:
            filterTreeByType(value,searchType)

def parse_transform(transform_str):
    """convert transforms into transformation matrix"""
    #print transform_str
    import re
    # regex for extracting numbers from transform string
    scanfloat =  r"[+\-]?(?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+)?"
    tr = None;tr_pos = None
    mt = None;mt_pos = None
    sc = None;sc_pos = None
    ##################
    if 'translate' in transform_str:
        translate_str = re.findall(r'translate\(.*?\)',transform_str)[0]
        txy = re.findall(scanfloat,translate_str)
        if type(txy) is list and len(txy) == 2:
            tx,ty = txy
        else: # deal with rare situation of exact resizing
            tx = txy[0]
            ty = txy[0]
        tr = np.array([[1.,0,float(tx)],
                       [0,1.,float(ty)],
                       [0,0,1.        ]])
        tr_pos = transform_str.find('translate')
    ##################
    if 'scale' in transform_str:
        translate_str = re.findall(r'scale\(.*?\)',transform_str)[0]
        sx,sy = re.findall(scanfloat,translate_str)
        sc = np.array([[float(sx),0,         0],
                       [0,        float(sy), 0],
                       [0,        0,        1.]])
        sc_pos = transform_str.find('scale')
    ##################
    if 'matrix' in transform_str:
        matrix_str = re.findall(r'matrix\(.*?\)',transform_str)[0]
        a,b,c,d,e,f = re.findall(scanfloat,matrix_str)
        a,b,c,d,e,f = [float(s) for s in [a,b,c,d,e,f]]
        mt = np.array([[a,c,e],
                       [b,d,f],
                       [0,0,1.]])
        mt_pos = transform_str.find('matrix')
    ##################
    tr_pos = {False:tr_pos,True:0}[tr_pos is None]
    mt_pos = {False:mt_pos,True:0}[mt_pos is None]
    sc_pos = {False:sc_pos,True:0}[sc_pos is None]
    s = [tr_pos,mt_pos,sc_pos]
    def take0(x):
        return x[0]
    trnsfrms = [mtrx for pos,mtrx in sorted(zip(s,[tr,mt,sc]),key =take0)]
    trnsfrms = [m for m in trnsfrms if not(m is None)]
    from numpy import dot
    from functools import reduce
    if len(trnsfrms) >= 1:
        mtrx = reduce(lambda x,y:dot(x,y.T),trnsfrms)
    return mtrx

def get_transforms(node,tlist = []):
    """get the list of transforms applied to a given node, walking up the svg
    tree to fill tlist. Pass an empyt list to call"""
    if node.hasAttribute('transform'):
        #print node.toxml()
        tlist.extend([parse_transform(node.getAttribute('transform'))])
    if not(node.nodeName == 'svg'):
        return get_transforms(node.parentNode,tlist)
    else:
        return([t for t in tlist if not(t is None)])

class FFItem(dict,object):
    """ base class for figurefirst objects that will be converted to matplotlib
    objects eg. axes"""
    def __init__(self,tagnode,**kwargs):
        self.tagnode = tagnode
        self.node = tagnode.parentNode
        self.id = self.node.getAttribute('id')
        self.name = tagnode.getAttribute('figurefirst:name')
        self.ismplaxis = False
        self.ismplfigure = False
        if self.node.hasAttribute('transform'):
            self.transform_str = self.node.getAttribute('transform')
        else:
            self.transform_str = None

class FFSVGItem(FFItem,object):
    """base class for svg objects that figurefirst will manipulate in
    the native svg form eg. text and paths. These objects can be used
    to change the style of tagged graphics in the document"""
    def __init__(self,tagnode):
        super(FFSVGItem,self).__init__(tagnode)
        if self.node.tagName != 'circle':
            x = float(self.node.getAttribute('x'))
            y = float(self.node.getAttribute('y'))
            h = float(self.node.getAttribute('height'))
            w = float(self.node.getAttribute('width'))
        else:
            x = float(self.node.getAttribute('cx'))
            y = float(self.node.getAttribute('cy'))
            h = float(self.node.getAttribute('r'))*2
            w = float(self.node.getAttribute('r'))*2
        self.p1 = np.array([x,y,1])
        self.p2 = np.array([x+w,h+y,1])
        self.load_style()

    def __getattr__(self,attr):
        if attr == 'x':
            return self.p1[0]
        if attr == 'y':
            return self.p1[1]
        if attr == 'w':
            return (self.p2-self.p1)[0]
        if attr == 'h':
            return (self.p2-self.p1)[1]
        if attr == 'r':
            return (self.p2-self.p1)[0]/2.

    def load_style(self):
        self.loaded_attr = dict()
        [self.loaded_attr.update({k:v}) for k,v in self.node.attributes.items()]
        self.style = dict()
        style_list =  self.loaded_attr['style'].split(';')
        style_list = [x for x in style_list if len(x)>0]
        [self.style.update({x.split(':')[0]:x.split(':')[1]}) for x in style_list]

    def frmtstyle(self):
        return ';'.join(['%s:%s'%(k,v) for k,v in self.style.items()])

class FFSVGPath(FFSVGItem,object):
    """ represents a svg path, currently figurefirst is unable to change the dimensions of the
    path, and the x, y, w, h attributes are meaningless placeholders"""
    def __init__(self,tagnode):
        super(FFSVGItem,self).__init__(tagnode)
        self.d_str = self.node.getAttribute('d')
        self.load_style()
        self.p1 = np.array([0,0,1])
        self.p2 = np.array([0,0,1])

    def __getattr__(self,attr):
        if attr == 'x':
            return self.p1[0]
        if attr == 'y':
            return self.p1[1]
        if attr == 'w':
            return (self.p2-self.p1)[0]
        if attr == 'h':
            return (self.p2-self.p1)[1]

    def load_style(self):
        self.loaded_attr = dict()
        [self.loaded_attr.update({k:v}) for k,v in self.node.attributes.items()]
        self.style = dict()
        style_list =  self.loaded_attr['style'].split(';')
        style_list = [x for x in style_list if len(x)>0]
        [self.style.update({x.split(':')[0]:x.split(':')[1]}) for x in style_list]

    def frmtstyle(self):
        return ';'.join(['%s:%s'%(k,v) for k,v in self.style.items()])

class FFSVGText(FFSVGItem,object):
    """ represents a svg text object, you can change the text, font as well
    as styling x,y contain the orign of the text box, height and with are
    currently not implemented since that would require parsing the font info"""

    def __init__(self,tagnode):
        super(FFSVGItem,self).__init__(tagnode)
        #print 'here'
        x = float(self.node.getAttribute('x'))
        y = float(self.node.getAttribute('y'))
        self.p1 = np.array([x,y,1])
        #self.p1 = np.array([0,0,1])
        self.p2 = np.array([0,0,1])
        ## need to implement h and width
        #h = float(self.node.getAttribute('height'))
        #w = float(self.node.getAttribute('width'))
        #self.p1 = np.array([x,y,1])
        #self.p2 = np.array([x+w,h+y,1])
        self.load_style()
        self.load_text()
        self.node.getElementsByTagName('tspan')[0].childNodes[0]

    def load_style(self):
        self.loaded_attr = dict()
        [self.loaded_attr.update({k:v}) for k,v in self.node.attributes.items()]
        self.style = dict()
        style_list =  self.loaded_attr['style'].split(';')
        style_list = [x for x in style_list if len(x)>0]
        [self.style.update({x.split(':')[0]:x.split(':')[1]}) for x in style_list]

    def load_text(self):
        self.text = self.node.getElementsByTagName('tspan')[0].childNodes[0].data

    def __getattr__(self,attr):
        if attr == 'x':
            return self.p1[0]
        if attr == 'y':
            return self.p1[1]
        if attr == 'w':
            warn('FFSVGtext object width attribute not implemented')
            return (self.p2-self.p1)[0]
        if attr == 'h':
            warn('FFSVGtext object height attribute not implemented')
            return (self.p2-self.p1)[1]

class FFSVGGroup(FFItem,object):
    """ used to collect groups of svg items"""
    def __init__(self,tagnode,**kwargs):
        super(FFSVGGroup,self).__init__(tagnode,**kwargs)

    def __getattr__(self,attr):
        try:
            pnts = np.vstack([np.array([np.array([i.x,i.y]),np.array([i.x+i.w,i.y+i.h])])
                              for i in self.values()])
        except ValueError:
            raise NameError('Could not find an axis for this figure. You probably have a figurefirst:figure tag with no axes associated with it.')

        x = np.min(pnts[:,0])
        y = np.min(pnts[:,1])
        w = np.max(pnts[:,0])-x
        h = np.max(pnts[:,1])-y
        try:
            return {'x':x,'y':y,'w':w,'h':h}[attr]
        except KeyError:
            return self.__getattribute__(attr)

class FFGroup(FFItem,object):
    """ used to collect groups objects that will be translated into matplotlib objects
    eg. axes and figures, x,y w and h is the collective x,y width and height of all the
    enclosed objects"""
    def __init__(self,tagnode,**kwargs):
        super(FFGroup,self).__init__(tagnode,**kwargs)

    def __getattr__(self,attr):
        #try:
        vals = [np.array([np.array([i.x,i.y]),np.array([i.x+i.w,i.y+i.h])])
                              for i in self.values()]
        #print(attr)
        if len(vals)>0:
            pnts = np.vstack([np.array([np.array([i.x,i.y]),np.array([i.x+i.w,i.y+i.h])])
                              for i in self.values()])
            x = np.min(pnts[:,0])
            y = np.min(pnts[:,1])
            w = np.max(pnts[:,0])-x
            h = np.max(pnts[:,1])-y
            try:
                return {'x':x,'y':y,'w':w,'h':h}[attr]
            except KeyError:
                #return self.__dict__[attr]
                return super(FFGroup, self).__getattribute__(attr)
                #return self.__getattribute__(attr)
        else:
            pnts = None
            return self.__getattribute__(attr)
        #except ValueError:
        #    raise NameError('Could not find an axis for this figure. You probably have a figurefirst:figure tag with no axes associated with it.')


class FFFigure(FFGroup,object):
    """ Represents a matplotlib figure """
    def __init__(self,tagnode,**kwargs):
        if not(tagnode == None):
            super(FFFigure,self).__init__(tagnode,**kwargs)
        self.ismplfigure = False

    def __getattr__(self,attr):
        try:
            if attr is 'ismplfigure':
                return False
            val = super(FFFigure,self).__getattr__(attr)
            return val
        except AttributeError:
            if self.ismplfigure == True:
                return self.figure.__getattribute__(attr)
                #return self['figure'].__getattribute__(attr)
            else:
                return self.__getattribute__(attr)

class FFTemplateTarget(FFFigure,object):
    """represtents the target of a template. The all the axes within the template
     figure will be scaled to fit within the template target box"""

    def __init__(self,tagnode,**kwargs):
        self.template_source = tagnode.getAttribute('figurefirst:template')
        super(FFTemplateTarget,self).__init__(tagnode,**kwargs)
        x = float(self.node.getAttribute('x'))
        y = float(self.node.getAttribute('y'))
        h = float(self.node.getAttribute('height'))
        w = float(self.node.getAttribute('width'))
        self.p1 = np.array([x,y,1])
        self.p2 = np.array([x+w,h+y,1])


    def __getattr__(self,attr):
        if attr == 'x':
            return self.p1[0]
        if attr == 'y':
            return self.p1[1]
        if attr == 'w':
            return (self.p2-self.p1)[0]
        if attr == 'h':
            return (self.p2-self.p1)[1]
        else:
            try:
                val = super(FFTemplateTarget,self).__getattr__(attr)
                return val
            except AttributeError:
                if self.ismplfigure == True:
                    return self['figure'].__getattribute__(attr)
                else:
                    return self.__getattribute__(attr)

class FFAxis(FFItem):
    """ Stores the data requred for the creation of a matplotlib axes
    as specified by the layout """

    def __init__(self,tagnode,**kwargs):
        super(FFAxis, self).__init__(tagnode,**kwargs)
        x = float(self.node.getAttribute('x'))
        y = float(self.node.getAttribute('y'))
        h = float(self.node.getAttribute('height'))
        w = float(self.node.getAttribute('width'))
        self.p1 = np.array([x,y,1])
        self.p2 = np.array([x+w,h+y,1])
        self.record = False # if this is true, it will save all matplotlib calls to the datafile

    def __getattr__(self,attr):
        if attr == 'x':
            return self.p1[0]
        if attr == 'y':
            return self.p1[1]
        if attr == 'w':
            return (self.p2-self.p1)[0]
        if attr == 'h':
            return (self.p2-self.p1)[1]
        else:
            if attr is 'ismplaxis':
                return self.__getattribute__(attr)
            if self.ismplaxis:
                data_filename = self.breadcrumb['data_filename']
                layout_filename = self.breadcrumb['layout_filename']
                layout_key = self.breadcrumb['layout_key']

                # wrap custom functions as if they are matplotlib functions
                # functions must have form: func(ax, *args, *kwargs)
                # Two options:
                #     (1) Self contained function, which will be pickled into the data file
                #     (2) String pointing to a package.module.function (package.module.submodule.function okay too)
                # syntax: (1) _custom
                #         (2) first argument is a list
                #             - if not empty: first element is a unique title,
                #                             additional elements should describe the arguments (in order)
                #                             argument descriptions are not required
                #             - if empty: title is set to function name. duplicate titles are deleted in the data file
                #                         thus, for non-unique function calls, it is necessary to specify a title
                #         (3) second argument is either a function (which will be pickled) or a string of a full package.module.function path
                # example: self._plot(['Unique Title', 'Time', 'Response'],
                #                     user_defined_function, *args, **kwargs)
                if PY3 and attr == '_custom':
                    def custom_wrapper(*args, **kwargs):
                        info = args[0]
                        title = args[1]
                        args_description = []
                        if len(info) > 0:
                            title = info[0]
                            if len(info) > 1:
                                args_description = info[1:]
                        function = args[1]
                        package = 'custom'
                        regenerate.__save_fifidata__(data_filename, layout_key,
                                                     package, function,
                                                     title, args_description,
                                                     *args[2:], **kwargs)
                        f = regenerate.__load_custom_function__(package, function)
                        f(self['axis'], *args[2:], **kwargs)
                    return custom_wrapper


                # wrap matplotlib methods and figurefirst.mpl_functions and save data to a pickle file
                # syntax: (1) call: prepend '_' to function call (eg. '_plot', '_set_xlim', '_adjust_spines')
                #         (2) first argument is a list
                #             - if not empty: first element is a unique title,
                #                             additional elements should describe the arguments (in order)
                #                             argument descriptions are not required
                #             - if empty: title is set to function name. duplicate titles are deleted in the data file
                #                         thus, for non-unique function calls, it is necessary to specify a title
                # example: self._plot(['Unique Title', 'Time', 'Response'], *args, **kwargs)
                #
                # notes: add_artist does not work, other functions like linecollections etc. might not work either?
                elif PY3 and attr[0] == '_':
                    function = attr[1:]
                    if function in mpl_functions.__dict__.keys():
                        def figurefirst_wrapper(*args, **kwargs):
                            info = args[0]
                            title = attr[1:]
                            args_description = []
                            if len(info) > 0:
                                title = info[0]
                                if len(info) > 1:
                                    args_description = info[1:]
                            package = 'figurefirst'
                            function = attr[1:]
                            regenerate.__save_fifidata__(data_filename, layout_key,
                                                         package, function,
                                                         title, args_description,
                                                         *args[1:], **kwargs)
                            f = regenerate.__load_custom_function__(package, function)
                            f(self['axis'], *args[1:], **kwargs)
                        return figurefirst_wrapper
                    else:
                        def mpl_wrapper(*args, **kwargs):
                            info = args[0]
                            title = attr[1:]
                            args_description = []
                            if len(info) > 0:
                                title = info[0]
                                if len(info) > 1:
                                    args_description = info[1:]
                            package = 'matplotlib'
                            function = attr[1:]
                            if not regenerate.__is_mpl_call_saveable__(function):
                                s = 'Function name: ' + function + ' cannot be saved. Try finding a replacement in figurefirst.mpl_functions, or define your own custom wrapper'
                                raise ValueError(s)
                            regenerate.__save_fifidata__(data_filename, layout_key,
                                                         package, function,
                                                         title, args_description,
                                                         *args[1:], **kwargs)
                            self['axis'].__getattribute__(attr[1:])(*args[1:], **kwargs) # This calls a matplotlib method
                        return mpl_wrapper



                # regular matplotlib or figurefirst.mpl_functions call, will only be recorded if self.record = True
                else:
                    if not PY3:
                        return self['axis'].__getattribute__(attr)
                    else:
                        if not self.record:
                            return self['axis'].__getattribute__(attr)
                        else:
                            if attr in mpl_functions.__dict__.keys():
                                def wrapper(*args, **kwargs):
                                    title = attr
                                    args_description = []
                                    package = 'figurefirst'
                                    function = attr
                                    regenerate.__save_fifidata__(data_filename, layout_key,
                                                                 package, function,
                                                                 title, args_description,
                                                                 *args, **kwargs)
                                    f = regenerate.__load_custom_function__(package, function)
                                    f(self['axis'], *args, **kwargs)
                            else:
                                def wrapper(*args, **kwargs):
                                    title = attr
                                    package = 'matplotlib'
                                    function = attr
                                    args_description = []
                                    if not regenerate.__is_mpl_call_saveable__(function):
                                        s = 'Function name: ' + function + ' cannot be saved. Try finding a replacement in figurefirst.mpl_functions, or define your own custom wrapper, or turn off record.'
                                        raise ValueError(s)
                                    regenerate.__save_fifidata__(data_filename, layout_key,
                                                                 package, function,
                                                                 title, args_description,
                                                                 *args, **kwargs)
                                    self['axis'].__getattribute__(attr)(*args, **kwargs) # This calls a matplotlib method
                            return wrapper

            else:
                return self.__getattribute__(attr)

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


class FigureLayout(object):
    """ autogenlayers - if True, figurefirst will automatically create targetlayers in the svg for each figure,
    default: True make_mplfigures - if True, figurefirst will call self.make_mplfigures() during init dpi - default 300,
    which is desired for print figures hide_layers - list of inkscape layer names you want to set to
    invisible (e.g. your template layers) construct an object that specifies the figure layout fom the svg file layout_filename.
    """

    def __init__(self, layout_filename, autogenlayers=True,make_mplfigures = False, dpi=300, hide_layers=['Layer 1']):
        self.dpi = dpi # should be 300 for print figures
        self.autogenlayers = autogenlayers
        self.layout_filename = os.path.join(layout_filename)
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
        self.data_filename = self.layout_filename.split('.svg')[0]+'_data.dillpickle'

        try:
            figuretree,grouptree,leafs,svgitemtree = self.make_group_tree()
            self.axes = leafs
            self.figures = figuretree
            self.axes_groups = grouptree
            self.svgitems = svgitemtree
            self.load_pathspecs()
        except AttributeError:
            pass #print('Warning: No rectangles in Document!')
        except KeyError:
            print('Warning: key error - probably loading a layout with missing links, like missing figurefirst:template targets.')
        #add the spinespecs
        for ax in self.axes.values():
            if not(ax.node is None):
                for node in ax.node.childNodes:
                    if node.nodeType == 1:
                        if node.tagName == 'figurefirst:spinespec':
                            ax.spinespec = node.getAttribute('figurefirst:spinelist')
            #self.load_svgitems()

        # dont allow sx and sy to differ
        # inkscape seems to ignore inconsistent aspect ratios by
        # only using the horizontal element of the viewbox, but
        # it is probably best to assert that the a.r's are the same
        # for now
        #assert self.layout_user_sx == self.layout_user_sy
        if np.abs(self.layout_user_sx[0] - self.layout_user_sy[0]) > figurefirst_user_parameters.rounding_tolerance:
            warnings.warn("""The the scaling of the user units in x and y are different and may result in unexpected
                            behavior. Make sure that the aspect ratio defined by the viewbox attribute of the root
                            SVG node is the same as that given by the document hight and width.""")
        if make_mplfigures:
            self.make_mplfigures()

        for layer in hide_layers:
            self.set_layer_visibility(layer, False)

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

    def make_group_tree(self):
        """ does the work of traversing the svg document and building the representation
        of figures, groups and axes, this needs to be done before self.makemplfigures
        can generate the matplotlib figurs"""
        def traverse_axes(node,grouptree):
            gname = None
            axname = None
            tree_loc = grouptree
            for child in node.childNodes:
                if child.nodeType == 1:
                    if child.tagName in ['figurefirst:group']:
                        grp = FFGroup(child)
                        grouptree[grp.name] = grp
                        tree_loc = grouptree[grp.name]
                    if child.tagName in ['figurefirst:axis']:
                        ax = FFAxis(child)
                        grouptree[ax.name] = ax
                        mpl_methods_elements = node.getElementsByTagName('figurefirst:mplmethods')
                        mpl_methods = dict()
                        grouptree[ax.name].mplmethods = mpl_methods
                        for mpl_methods_element in mpl_methods_elements:
                            [grouptree[ax.name].mplmethods.update({key:value}) for key,value in mpl_methods_element.attributes.items()]
                        projection = node.getElementsByTagName('figurefirst:projection')
                        if child.hasAttribute('figurefirst:projection'):
                            grouptree[ax.name].projection = child.getAttribute('figurefirst:projection')
                        else:
                            grouptree[ax.name].projection = 'rectilinear'
                        if child.hasAttribute('figurefirst:spinespec'):
                            grouptree[ax.name].spinespec = child.getAttribute('figurefirst:spinespec')
                    if child.tagName in ['figurefirst:figure']:
                        if child.hasAttribute('figurefirst:template'):
                            fig = FFTemplateTarget(child)
                            grouptree[fig.name] = fig
                        else:
                            fig = FFFigure(child)
                            grouptree[fig.name] = fig
                            tree_loc = grouptree[fig.name]
                    #if child.tagName in ['figurefirst:svgitem']:
                    #    if node.tagName == 'path':
                    #        item = FFSVGPath(child)
                    #    elif node.tagName == 'text':
                    #        item = FFSVGText(child)
                    #    else:
                    #        item = FFSVGItem(child)
                    #    grouptree[item.name] = item
            for child in node.childNodes:
                if child.hasChildNodes():
                    traverse_axes(child,tree_loc)


        def traverse_svgitems(node,svgtree):
            gname = None
            axname = None
            tree_loc = svgtree
            for child in node.childNodes:
                if child.nodeType == 1:
                    if child.tagName in ['figurefirst:svggroup']:
                        grp = FFSVGGroup(child)
                        svgtree[grp.name] = grp
                        tree_loc = svgtree[grp.name]
                    if child.tagName in ['figurefirst:svgitem']:
                        if node.tagName == 'path':
                            item = FFSVGPath(child)
                        elif node.tagName == 'text':
                            item = FFSVGText(child)
                        else:
                            item = FFSVGItem(child)
                        svgtree[item.name] = item
            for child in node.childNodes:
                if child.hasChildNodes():
                    traverse_svgitems(child,tree_loc)

        ### Create the group tree
        grouptree = dict()
        traverse_axes(self.layout,grouptree)

        svgitemtree = dict()
        traverse_svgitems(self.layout,svgitemtree)
        #filterTreeByType(grouptree,FFSVGPath)
        leafs = flatten_dict(grouptree)

        #extract the axes from the rest of the svgitems
        axtree = extractTreeByType(grouptree,FFAxis)
        #svgitemtree = extractTreeByType(grouptree,FFSVGItem)

        ### Create the figure tree
        figuretree = dict()
        figuretree['none'] = FFFigure(None)
        for val in grouptree.values():
            if isinstance(val,FFFigure):
                figuretree[val.name] = val
            else:
                figuretree['none'][val.name] = val

        ### Compose the transforms
        from numpy import dot
        from functools import reduce
        for leafname,leaf in leafs.items():
            tlist = get_transforms(leaf.node,[])
            tlist.reverse()
            leaf.tlist = tlist
            if len(tlist) > 0:
                mtrx = reduce(lambda x,y:dot(x,y),tlist)
                leaf.mtrx = mtrx
            else:
                leaf.mtrx = np.diag(np.ones(3))
            leaf.p1 = np.dot(leaf.mtrx,leaf.p1)
            leaf.p2 = np.dot(leaf.mtrx,leaf.p2)
            #svg origin is at top left
            leaf.p1[1] = self.layout_uh-leaf.p1[1]
            leaf.p2[1] = self.layout_uh-leaf.p2[1]
            #Deal with any vector flippage
            sp = np.vstack([leaf.p1,leaf.p2])
            tp1 = np.min(sp,axis = 0);tp2 = np.max(sp,axis = 0)
            leaf.p1 = tp1;leaf.p2 = tp2
            ### need to add error condition for points that are outside the figure bounds

        ### Populate the template targets
        for key,l in leafs.items():
            if type(l) == FFTemplateTarget:
                import copy
                #for k,v in figuretree[l.template_source].items():
                #try:
                figuretree[l.template_source].node = None
                figuretree[l.template_source].tagnode = 'None'
                for value,item in figuretree[l.template_source].items():
                    item.node = None
                    item.tagnode = 'None'
                newv = copy.deepcopy(figuretree[l.template_source])
                #except RuntimeError:

                vleafs = flatten_dict(newv)
                origin = np.array([newv.x,newv.y,1])
                sx = l.w/newv.w; sy = l.h/newv.h
                for vleaf in vleafs.values():
                    t1 = (vleaf.p1-origin)*np.array([sx,sy,0]) + l.p1
                    t2 = t1 + np.array([vleaf.w*sx,vleaf.h*sy,0])
                    vleaf.p1 = t1; vleaf.p2 = t2
                    l[vleaf.name] = vleaf

        ### Re-folliate
        leafs = flatten_dict(figuretree)
        #print leafs
        new_leafs = dict()
        for key,value in leafs.items():
            if isinstance(value,FFAxis):
                #if len(key) ==1:
                if key[0] == 'none':
                    if len(key) == 1:
                        pass
                    elif len(key) == 2:
                        new_leafs[key[1]] = value
                    else:
                        new_leafs[tuple(key[1:])] = value
                else:
                    new_leafs[key] = value
        axtree = figuretree
        return figuretree,axtree,new_leafs,svgitemtree

    def load_svgitems(self):
        """loads the svgitems from the layout document"""
        self.svgitems = dict()
        elementlist = self.layout.getElementsByTagNameNS(XMLNS, 'svgitem')
        itemlist = [SVGItem(el,self) for el in elementlist]
        [self.svgitems.update({sp.name:sp}) for sp in itemlist]

    def load_pathspecs(self):
        """parses pathspec objects from the layout document"""
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
        """returns dictionary of layers in teh output file"""
        output_svg = self.output_xml.getElementsByTagName('svg')[0]
        layers = get_elements_by_attr(output_svg,"inkscape:groupmode",'layer')
        layerdict = {}
        for l in layers:
            label = attributes['inkscape:label'].value
            layerdict[label] = l
        return layerdict

    def set_layer_visibility(self,inkscape_label = 'Layer 1',vis = True,gid = None,):
        """appled to the output svg usefull to hide the design layers on the
        newly created figures"""
        import re
        value = {False:'none',True:'inline'}[vis]
        output_svg = self.output_xml.getElementsByTagName('svg')[0]
        layers = get_elements_by_attr(output_svg,"inkscape:groupmode",'layer')
        for l in layers:
            if l.attributes['inkscape:label'].value == inkscape_label:
                try:
                    style_str = l.attributes['style'].value
                except:
                    l.setAttribute('style', "display:none")
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
        """finds the xmlnode with a given figurefirst:name tag"""
        figure_elements = self.layout.getElementsByTagNameNS(XMLNS, 'figure')
        figure_elements_by_name_dict = {}
        for figure_element in figure_elements:
            figname = figure_element.getAttribute('figurefirst:name')
            figure_elements_by_name_dict[figname] = figure_element
        return figure_elements_by_name_dict[name]

    def make_mplfigures(self, hide=False):
        """generates  matplotlib figures from the tree of parsed FFFigure and FFGroup,
        FFTemplatetargets"""
        for figname,figgroup in self.figures.items():
            if len(figgroup.keys()):
                leafs = flatten_dict(figgroup)
                fw_in = tounit(self.layout_width, 'in')
                fh_in = tounit(self.layout_height, 'in')
                fig = plt.figure(figsize=(fw_in, fh_in))
                for leafkey,leaf in leafs.items():
                    left = leaf.x/self.layout_uw
                    width = leaf.w/self.layout_uw
                    height = leaf.h/self.layout_uh
                    bottom = leaf.y/self.layout_uh
                    if type(leaf) == FFAxis:
                        leaf['axis'] = fig.add_axes([left, bottom, width, height],projection = leaf.projection,label = '-'.join(leafkey))
                        leaf['figname'] = figname
                        leaf.ismplaxis = True
                        figgroup.figure = fig
                        #figgroup['figure'] = fig
                        figgroup.ismplfigure = True
                    else:
                        pass
                        #print type(leaf)
            if hide:
                plt.close()

        self.make_breadcrumbs_for_axes()

    def append_figure_to_layer(self, fig, fflayername,
                               cleartarget=figurefirst_user_parameters.cleartarget,
                               save_traceback=figurefirst_user_parameters.save_traceback,
                               notes=None):
        """inserts a figure object, fig, into an inkscape SVG layer, the layer fflayername should be
        taged with a figurefirst:targetlayer tag. if fflayername is not found then a targetlayer is generated so
        long as self.autogenlayers is set to True, the default. If cleartarget is set to True then the contents of the
        target layer will be removed, usefull for itterative figure design.

        save_traceback - save the traceback stack to the figure's xml. This makes it easy to find out what function was
                         used to generate the figure. Also saves date modified

        notes - string, which is added as an attribute to the xml of the layer. Helpful if you want to embed info into the
                layers for future reference.

        """


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
                #print('Created new layer: %s'%(fflayername))
                target_layer, found_target = get_target_layer(fflayername)
            else:
                target_layer = target_layers[0]
                #print('targetlayer %s not found inserting into %s'%(fflayername,target_layer.getAttribute('figurefirst:name')))
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
            print('unable to pass axes gid to svg')

        if save_traceback:
            tb = traceback.extract_stack()
            tb_formatted = traceback.format_list(tb)
            self.add_attribute_to_layer(fflayername, 'figurefirst:traceback', tb_formatted)
            time_str = time.strftime("%b %d %Y %H:%M:%S", time.localtime(time.time())) + ' ' + time.strftime("%Z", time.gmtime())
            self.add_attribute_to_layer(fflayername, 'figurefirst:date-modified', time_str)
        if notes:
        	self.add_attribute_to_layer(fflayername, 'figurefirst:notes', notes)

    def add_attribute_to_layer(self, layer_name, attribute, value):
        output_svg = self.output_xml.getElementsByTagName('svg')[0]
        layers = get_elements_by_attr(output_svg,"inkscape:groupmode",'layer')
        for layer in layers:
            if layer_name == layer.getAttribute('id') or layer_name == layer.getAttribute('inkscape:label'):
                svg_layer = layer
                svg_layer.setAttribute( unicode(attribute), unicode(value))
                return
        s = 'Failed to find layer: ' + layer_name
        raise ValueError(s)

    def insert_figures(self, fflayername='mpl_layer',
                       cleartarget=figurefirst_user_parameters.cleartarget):
        """ takes a reference to the matplotlib figure and saves the
        svg data into the target layer specified with the xml tag <figurefirst:targetlayer>
        this tag must have the attribute figurefirst:name = fflayername"""
        for fig in self.figures.values():
            if fig.ismplfigure:
                self.append_figure_to_layer(fig, fflayername, cleartarget=cleartarget)
            else:
                print(fig.__dict__)

    def apply_mpl_methods(self):
        """ apply valid mpl methods to figure"""
        for mplax in self.axes.values():
            ax = mplax['axis']
            #if 'mplmethods' in mplax.keys():
            for key, value in mplax.mplmethods.items():
                if key.startswith('figurefirst:'):
                    potential_method = key.split('figurefirst:')[1]
                    try:
                        eval("ax."+potential_method+"("+value+")")
                            #print "ax."+potential_method+"("+value+")"
                            #getattr(ax, potential_method)(eval(value))
                    except AttributeError:
                        print(potential_method, 'is unknown method for mpl axes')

    def apply_svg_attrs(self, svg_items_to_update='all'):
        """applies attributes to svgitems eg. lw stroke ect... need to call
        this function before saving in order to propegate changes to svgitems

        svg_items_to_update - (optional) - provide a list of the svgitem tags that you wish to have updated. Default is 'all', which updates all the svgitems,
                                           which could reset svgitems whose attributes were not set since the last call to 'None'.
        """
        leafs = flatten_dict(self.svgitems)
        output_svg = self.output_xml.getElementsByTagName('svg')[0]
        for svgkey, svgitem in leafs.items():
            if svg_items_to_update != 'all':
                if svgkey[0] not in svg_items_to_update: # for some reason the svgkey is a tuple
                    continue
            nd = svgitem.node
            ndid = nd.getAttribute('id')
            outnd = get_elements_by_attr(output_svg,'id',ndid)[0]
            outnd.setAttribute('style',svgitem.frmtstyle())
            if isinstance(svgitem,FFSVGText):
                outnd.getElementsByTagName('tspan')[0].childNodes[0].data = svgitem.text
                outnd.getElementsByTagName('tspan')[0].setAttribute('style',svgitem.frmtstyle())

    def pass_xml(self, gid, key, value):
        """pass key, value pair xml pair to group with ID gid
        gid should contain prefix 'figurefirst:' to ensure uniqueness
        usage: layout.pass_xml(gid,'jessyink:effectIn', 'name:appear;order:1;length:800')"""

        if gid[:12] != 'figurefirst:':
            warn("""Warning: ID should start with 'figurefirst:'
                     because non-unique ids will cause silent failure in jessyink""")
        output_svg = self.output_xml.getElementsByTagName('svg')[0]
        elist = list()
        for gr in output_svg.getElementsByTagName('g'):
            if gr.attributes:
                test_list = gr.attributes.keys()
                if 'id' in test_list:
                    if gr.getAttribute('id') == gid:
                        elist.append(gr)
        if len(elist) > 1:
            print(len(elist), 'groups with mataching ID found')
        elif len(elist) == 0:
            print('ID not found')
        for el in elist:
            el.setAttribute(key, value)

    def to_svg_buffer(self, fig):
        """writes a matplotlib figure into a stringbuffer and returns the buffer"""
        if PY3:
            from io import StringIO
        else:
            from StringIO import StringIO
        fid = StringIO()
        #if fig.ismplfigure:
        fig.figure.savefig(fid, format='svg', transparent=True, dpi=self.dpi)
        fid.seek(0)
        return fid

    def write_svg(self, output_filename):
        """ writes the current output_xml document to output_filename"""
        try:
            outfile = open(output_filename, 'w')
            self.output_xml.writexml(outfile, encoding='utf-8')
        except UnicodeEncodeError:
            outfile.close()
            outfile = open(output_filename, 'w')
            outfile.write(self.output_xml.toxml().encode('ascii', 'xmlcharrefreplace'))
            outfile.close()

    def save(self,filename,hidelayers = [],targetlayer = None,fix_meterlimt= True):
        """convenience function, inserts layers and then calls
        wirte_svg to save"""
        if targetlayer:
            self.insert_figures(fflayername=targetlayer)
        else:
            self.insert_figures()
        for l in hidelayers:
            self.set_layer_visibility(l,False)
        self.write_svg(filename)
        from . import mpl_functions
        if fix_meterlimt:
            mpl_functions.fix_mpl_svg(filename)

    def clear_fflayer(self, fflayername):
        '''
        If inserting mpl figure into a mpl target layer that has stuff in it,
        e.g. old mpl data, use this function to clear the layer of any children
        except the figurefirst:targetlayer node.
        '''
        target_layers = self.output_xml.getElementsByTagNameNS(XMLNS, 'targetlayer')
        target_layer = None
        for tl in target_layers:
            if tl.getAttribute('figurefirst:name') == fflayername:
                target_layer = tl.parentNode
        if target_layer is None:
            return # no target found
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
                    if 1:
                        if child.nodeName != 'figurefirst:targetlayer':
                            # print('Removing node: '+ child.nodeName)
                            target_layer.removeChild(child)
                            removed_children += 1
                        else:
                            pass
                            # print 'Not removing: ', child.nodeName

    def make_breadcrumbs_for_axes(self):
        '''
        Save layout.svg, data.svg, figure, axis information into each mpl axis
        '''

        breadcrumb = {'layout_key': None,
                      'layout_filename': self.layout_filename,
                      'data_filename': self.data_filename}
        for key, axis in self.axes.items():
            breadcrumb_copy = copy.deepcopy(breadcrumb)
            key_copy = (k for k in key)
            breadcrumb_copy['layout_key'] = tuple(key_copy)
            axis.breadcrumb = breadcrumb_copy

    def write_fifidata(self, info, *args, **kwargs):
        '''
        Write arbitrary data to the figurefirst data file
        info - list of strings, e.g. ['title', 'description 1', 'description 2']
        args - data you want to store in the data file
        '''
        print (self.data_filename)
        regenerate.__save_fifidata__(self.data_filename, 'Supplemental Data',
                                     'none', 'none',
                                     info[0], info[1:],
                                     *args, **kwargs)
