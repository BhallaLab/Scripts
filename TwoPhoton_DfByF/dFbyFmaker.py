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
import scipy.stats as stat
import os
import sys
import glob


logger = logging.getLogger('')

#raw_ = cv2.namedWindow( 'raw' )
#edge = cv2.namedWindow( 'edge' )

save_direc_ = None

def init( ):
    global save_direc_
    save_direc_ = os.path.join( '.', os.path.split(c.args_.file)[1])
    if os.path.isdir( save_direc_ ):
        return
        for f in glob.glob( '%s/*' % save_direc_ ):
            os.remove(f)
    else:
        logging.info("Creating dir %s for saving data" % save_direc_)
        os.makedirs( save_direc_ )

def get_frame_data( frame ):
    img = np.array(frame)
    return img

def to_grayscale( img ):
    if img.max() >= 256.0:
        logging.debug("Converting image to grayscale")
        logging.debug("Max=%s, min=%s, std=%s"% (img.max(), img.min(),
            img.std()))
        img = 255 * ( img / float( img.max() ))
    gimg = np.array(img, dtype=np.uint8)
    return gimg

def get_edges( frame ):
    cannyFrame = to_grayscale( frame )
    edges = cv2.Canny( cannyFrame, c.elow, c.ehigh)
    return edges

def get_activity_vector( frames ):
    """Given a list of frames, return the indices of frames where there is an
    activity
    """
    meanActivity = [ x.mean() for x in frames ]
    # Now get the indices where peak value occurs. 
    activity = sig.argrelextrema( np.array(meanActivity), np.greater)[0]
    actFlie = os.path.join( save_direc_, 'activity_peak.csv')
    logging.info("Writing activity to %s" % actFlie)
    header = "frame index"
    np.savetxt(actFlie, activity, delimiter=',', header=header)
    return activity

def threshold_frame( frame, nstd = None):
    # Change the parameter to one's liking. Currently low threshold value is 3
    # std more than mean.
    mean = int(frame.mean())
    std = int(frame.std())
    if nstd is None:
        nstd = 3
    low = max(0, mean + (nstd * std))
    high = int( frame.max() )
    logging.info("Thresholding at %s + %s * %s" % (mean, nstd, std))
    logging.info("|-  low, high = %s, %s" % (low, high))
    frame = stat.threshold( frame, low, high, newval = 0)
    return to_grayscale( frame )

def save_figure( filename, img, **kwargs):
    """Store a given image to filename """
    global save_direc_ 
    img = to_grayscale( img )
    outfile = os.path.join( save_direc_, filename )
    logging.info( 'Saving image to %s ' % outfile )
    cv2.imwrite( outfile , img )
    return img

def get_roi( frames, window = 5):
    fShape = frames[0].shape
    activityVec = get_activity_vector( frames )

    # activityVec contains the indices where we see a local maxima of mean
    # activity e.g. most likely here we have a activity at its peak. Now we
    # collect few frames before and after it and do the rest.
    logger.debug("Activity vector: %s" % activityVec )
    allEdges = np.zeros( fShape )
    roi = np.zeros( fShape, dtype=np.uint8)
    for i in activityVec:
        low = max(0, i-window)
        high = min( fShape[0], i+window)
        bundle = frames[low:high]
        sumAll = np.zeros( fShape )
        for f in bundle:
            e = threshold_frame( f, nstd = 3)
            sumAll += e
        edges = get_edges( sumAll )
        save_figure( 'edges_%s.png' % i, edges, title = 'edges at index %s' % i)
        cellImg = compute_cells( edges )
        save_figure( 'cell_%s.png' % i, cellImg )
    allEdges += edges 
    save_figure( 'all_edges.png', allEdges, title = 'All edges')

def find_contours( img, **kwargs ):
    logger.debug("find_contours with option: %s" % kwargs)
    contours, h = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE )
    if kwargs.get('hull', True):
        logger.debug("Approximating contours with hull")
        contours = [ cv2.convexHull( x ) for x in contours ]

    if kwargs.get('filter', 0):
        contours = filter(lambda x:len(x) >= kwargs['filter'], contours)

    contourImg = None
    if kwargs.get('draw', False):
        contourImg = np.zeros( img.shape, dtype=np.uint8 )
        cv2.drawContours( contourImg, contours, -1, 255, 1)
    return contours, contourImg

def compute_cells( image ):
    # To compute the cells:
    # 0. hull <- Compute the convex hull with loose conditions.
    # 1. Compute the hull again of `hull`, if two hull are overlapping, we get a
    # cell.

    thresholdImg = threshold_frame( image, nstd = 0 )
    contours, contourImg = find_contours(thresholdImg
            , draw = True
            , filter = 1
            , hull = True
            )
    for c in contours:
        if len(c) < 5:
            continue
        cv2.ellipse( contourImg, cv2.fitEllipse(c), 255, 2 )
    return contourImg

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
    init( )
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
