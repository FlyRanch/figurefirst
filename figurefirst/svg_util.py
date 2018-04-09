#utility functions for dealing with svg files.

def replace_non_unique(in_filename,out_filename,
                       search_string = 'text_to_replace',
                       prefix = ''):
    """parse the document 'in_filename' and replace all 
    instances of the string 'search_string' with the 
    unique string 'prefix_x' where x is the occurance
    of the search_string"""
    with open(in_filename,'rt') as inf:
        strdta = inf.read()
        n_instances = strdta.count(search_string)
        for i in range(n_instances):
            strdta = strdta.replace(search_string, prefix + '_%s'%(i), 1)
        with open(out_filename,'wt') as outf:
            outf.write(strdta)