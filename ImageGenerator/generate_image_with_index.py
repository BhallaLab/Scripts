#!/usr/bin/env python

"""generate_image_with_index.py: 

Generates transparent image with numbers written on them. Can be used to
caliberate projectors for frame per seconds.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2015, Dilawar Singh and NCBS Bangalore"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"


import matplotlib.pyplot as plt
import os
import sys

fontsize = 100
dpi = 96
height = 768.0 / dpi
width = 1024.0 / dpi

if not os.path.exists('_images'):
    os.makedirs('_images')

for i in range(1000): 
    print("Creating image for %s" % i)
    fig = plt.figure( figsize=(width, height) )
    plt.axis('off')
    plt.plot()
    plt.figtext(0.4, 0.4, '%s' % i, fontsize=fontsize)
    plt.savefig('_images/%s.png' % i, dpi=dpi, transparent=True)
print("[INFO] All images are saved to _images")
