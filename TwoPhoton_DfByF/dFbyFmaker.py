#!/usr/bin/env python

"""dFbyFmaker.py: 

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2015, Dilawar Singh and NCBS Bangalore"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import config as c
import logging
from PIL import Image
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import cv2 
import time
import scipy.signal as sig

logger = logging.getLogger('')

#raw_ = cv2.namedWindow( 'raw' )
#edge = cv2.namedWindow( 'edge' )

def get_frame_data( frame ):
    img = np.array(frame)
    return img

def to_grayscale( frame ):
    frame = 255.0 * ( frame / float( frame.max() ))
    gimg = np.array(frame, dtype=np.uint8)
    return gimg

def get_edges( frame ):
    cannyFrame = to_grayscale( frame )
    edges = cv2.Canny( cannyFrame, c.low, c.high)
    return edges

def get_activity_vector( frames ):
    """Given a list of frames, return the indices of frames where there is an
    activity
    """
    meanActivity = [ x.mean() for x in frames ]
    # Now get the indices where peak value occurs. 
    activity = sig.argrelextrema( np.array(meanActivity), np.greater)
    return activity[0]

def get_roi( frames, window = 5):
    fShape = frames[0].shape
    activityVec = get_activity_vector( frames )

    # activityVec contains the indices where we see a local maxima of mean
    # activity e.g. most likely here we have a activity at its peak. Now we
    # collect few frames before and after it and do the rest.
    logger.debug("Activity vector: %s" % activityVec )
    for i in activityVec:
        low = max(0, i-window)
        high = min( fShape[0], i+window)
        bundle = frames[low:high]
        sumAll = np.zeros( fShape )
        for f in bundle:
            # e = get_edges( f )
            ret, e = cv2.threshold( to_grayscale(f), 127, 255, cv2.THRESH_BINARY)
            sumAll += e
        finalEdges = get_edges( to_grayscale(sumAll) )
        # Now draw contours and we are done.
        # cv2.imshow( 'final edges', finalEdges )
        contours, heirs = cv2.findContours( finalEdges
                , cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE 
                )
        plt.figure()
        plt.imshow( sumAll )
        plt.title("Activity in windows (%s,%s)" % (low, high))
        plt.show()
        # plt.figure( )
        # cv2.drawContours( sumAll, contours, -1, (255,0,0), 3)
        # plt.imshow( sumAll )
        # plt.show()

def process_tiff_file( tiff_file ):
    logger.info("Processing %s" % tiff_file)
    tiff = Image.open( tiff_file )
    frames = []
    try:
        i = 0
        while 1:
            i += 1
            tiff.seek( tiff.tell() + 1 )
            framedata = get_frame_data( tiff )
            frames.append( framedata )
    except EOFError as e:
        logger.info("All frames are processed")

    get_roi( frames )
            

def main( ):
    tiffFile = c.args_.file
    process_tiff_file( tiffFile )

if __name__ == '__main__':
    import argparse
    # Argument parser.
    description = '''description'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--file', '-f'
        , required = True
        , help = 'Tiff file to be passed'
        )
    parser.add_argument('--box', '-b'
        , required = False
        , default = "0,0,-1,-1"
        , type = str
        , help = 'Bounding box.'
        )
    parser.parse_args(namespace=c.args_)
    main()
