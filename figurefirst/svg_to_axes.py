#import set_params
#set_params.pdf()

from xml.dom import minidom
import matplotlib.pyplot as plt

def read_svg_to_axes(svgfile, width_inches=10):
    
    doc = minidom.parse(svgfile)
    
    print doc.firstChild.getAttribute('width')
    
    width_svg_pixels = float(doc.firstChild.getAttribute('width'))
    height_svg_pixels = float(doc.firstChild.getAttribute('height'))
    aspect_ratio = height_svg_pixels / float(width_svg_pixels)
    height_inches = width_inches*aspect_ratio

    fig = plt.figure(figsize=(width_inches, height_inches))
    
    rects = doc.getElementsByTagName('rect')
    
    axes = {}
    for rect in rects:
        
        x_px = float(rect.getAttribute("x"))
        y_px = float(rect.getAttribute("y"))
        width_px = float(rect.getAttribute("width"))
        height_px = float(rect.getAttribute("height"))
        label = str(rect.getAttribute("id"))
                
        left = x_px/width_svg_pixels
        width = width_px/width_svg_pixels
        height = height_px/height_svg_pixels
        bottom = (height_svg_pixels-y_px-height_px)/height_svg_pixels
        
        ax = fig.add_axes([left, bottom, width, height])
        axes.setdefault(label, ax)
        
    
    fig.savefig('/home/caveman/Desktop/testsvg_2.svg', format='svg')
    
    
    return fig, axes
    

        
