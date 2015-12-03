#!/usr/bin/env python

import cv2
import sys
import os
import pylab
import numpy as np

def check_for_circle( img, loc , threshold ):
    print("[INFO] Checking for a circle at %s" % str(loc) )
    mask = np.zeros(shape=(img.shape[0]+2, img.shape[1]+2), dtype=np.uint8)
    xy = (loc[1], loc[0])
    a = cv2.floodFill( img , mask , xy , 0 , loDiff=4)

def locate_circle( img, threshold ):
    maxPos = np.where( img >= img.max() - 1)
    for p in zip(*maxPos): 
        img[p] = 0
    maxPos = np.where( img == img.max())
    for p in zip(*maxPos): 
        check_for_circle( img, p , 20 )

    # print("[INFO] Drawing circle at : %s" % str(minL))
    # cv2.circle(img, minL, 100, 1, thickness=4)

def count( imgPath ):
    img = cv2.imread( imgPath, 0 )
    print("[INFO] min={0}, max={1}, avg={2}, std={3}".format(
        img.min(), img.max(), img.mean(), img.std())
        )
    threshold = img.min() + 0.6 * img.std()
    print("[INFO] Using threshold %s " % threshold)
    
    locate_circle( img, threshold )
    cv2.namedWindow("Final", cv2.WINDOW_NORMAL)
    cv2.imshow('Final', img)
    cv2.waitKey(0)

def search_edges_boundry( img ):
    edges = cv2.Canny( img, 60, 110)
    cv2.namedWindow("edges", cv2.WINDOW_NORMAL)
    cv2.imshow( "edges", edges)
    cv2.waitKey(0)

def main():
    imgPath = sys.argv[1]
    # count( imgPath )
    img = cv2.imread( imgPath, 0 )
    search_edges_boundry( img )

if __name__ == '__main__':
    main()
