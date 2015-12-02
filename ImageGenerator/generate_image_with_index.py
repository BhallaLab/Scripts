#!/usr/bin/env python

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
    plt.figtext(0.4, 0.25, '1', fontsize=fontsize)
    plt.savefig('_images/%s.png' % i, dpi=dpi, transparent=True)
print("[INFO] All images are saved to _images")
