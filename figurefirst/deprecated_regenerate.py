'''
Deprecated. This is here for legacy code. Ignore it.
'''

def mpl(function, layout, figure, axis, fifidatafile, title, args_description, *args, **kwargs):
    ax = layout.axes[(figure, axis)]
    info = [title]
    info.extend(args_description)
    ax.__getattr__('_'+function)(info, *args, **kwargs)

def custom(package, function, layout, figure, axis, fifidatafile, title, args_description, *args, **kwargs):
    ax = layout.axes[(figure, axis)]
    info = [title]
    info.extend(args_description)
    if package == 'figurefirst':
        ax.__getattr__('_'+function.split('.')[-1])(info, *args, **kwargs)
    else:
        print '==========================================='
        print package+'.'+function
        ax._custom(info, package+'.'+function, *args, **kwargs)

def mpl_patch(patch, layout, figure, axis, fifidatafile, title, args_description, *args, **kwargs):
    ax = layout.axes[(figure, axis)]
    info = [title]
    info.extend(args_description)
    ax._add_mpl_patch(info, *args, **kwargs)