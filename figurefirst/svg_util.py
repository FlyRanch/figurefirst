#utility functions for dealing with svg files.

def replace_non_unique(in_filename,out_filename,
                       search_string = 'text_to_replace',
                       prefix = ''):
    """parse the document 'in_filename' and replace all 
    instances of the string 'search_string' with the 
    unique string 'prefix_x'.

    Parameters
    ----------
    in_filename : name of the file to parse

    out_filename : name of the file to write. If 
        out_filename is the same as in_filename
        then the old document will be overwritten.

    search_string : target string to search and replace. Note: 
        when applying this function to svg layout documents
        take care that you don't target strings that are 
        common strings in the SVG language. e.g. 'label'

    prefix : the prefix will be appended with a number and used
        to replace each occurance of the search string.
     """

    with open(in_filename,'rt') as inf:
        strdta = inf.read()
        slist = strdta.split(search_string)
        outstr = ''.join([s + prefix + '_%s'%(i) for i,s in enumerate(slist[:-1])])
        outstr += slist[-1]
        with open(out_filename,'wt') as outf:
            outf.write(outstr)