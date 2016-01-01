#!/usr/bin/env python

__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2015, Dilawar Singh and NCBS Bangalore"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import config 
import logging
from PIL import Image
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import scipy.signal as sig
import scipy.stats as stat
import os
import sys
import glob
import datetime
import cv2
import helper

logger = logging.getLogger('')
shape_ = None
images_ = {}
save_direc_ = None

class Cell():
    def __init__(self, contour):
        self.contour = contour
        self.rectangle = cv2.boundingRect( contour )
        self.circle = cv2.minEnclosingCircle( contour )
        self.area = cv2.contourArea( contour ) * (config.args_.pixal_size ** 2.0)
        if len(contour) > 5:
            self.geometry = cv2.fitEllipse( contour )
            self.geometry_type = 'ellipse'
            axis = self.geometry[1]
            self.eccentricity = axis[0]/axis[1]
            self.radius = sum(axis) / 2.0
        else:
            self.geometry = cv2.minEnclosingCircle( contour )
            self.geometry_type = 'circle'
            self.eccentricity = 1.0
            self.radius = self.geometry[1]
            
        self.center = self.geometry[0]
        logging.debug("A potential cell : %s" % self)

    def __repr__(self):
        return "Center: %s, area: %s" % (self.center, self.area )

cells_ = []

def init( ):
    global save_direc_
    save_direc_ = os.path.join( '.', '_results_%s' % os.path.split(config.args_.file)[1])
    if os.path.isdir( save_direc_ ):
        return
        for f in glob.glob( '%s/*' % save_direc_ ):
            os.remove(f)
    else:
        logging.info("Creating dir %s for saving data" % save_direc_)
        os.makedirs( save_direc_ )

def get_frame_data( frame ):
    frame = frame.convert('L')
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
    edges = cv2.Canny( cannyFrame
            , config.elow, config.ehigh
            , L2gradient = True
            , apertureSize = config.canny_window_size
            )
    return edges

def get_activity_vector( frames ):
    """Given a list of frames, return the indices of frames where there is an
    activity
    """
    meanActivity = [ x.mean() for x in frames ]
    # Now get the indices where peak value occurs. 
    activity = sig.argrelextrema( np.array(meanActivity), np.greater)[0]
    # activity = activity[::3]
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
    logging.debug("Thresholding at %s + %s * %s" % (mean, nstd, std))
    logging.debug("|-  low, high = %s, %s" % (low, high))
    frame = stat.threshold( frame, low, high, newval = 0)
    return to_grayscale( frame )

def save_image( filename, img, **kwargs):
    """Store a given image to filename """
    global save_direc_ 
    global images_
    img = to_grayscale( img )
    outfile = os.path.join( save_direc_, filename )
    logging.info( 'Saving image to %s ' % outfile )
    cv2.imwrite( outfile , img )
    return img

def write_ellipses( ellipses ):
    global save_direc_
    outfile = os.path.join( save_direc_, 'bounding_ellipses.csv' )
    with open( outfile, 'w' ) as f:
        f.write("x,y,major,minor,rotation\n")
        for e in ellipses:
            (y, x), (minor, major), angle = e
            f.write('%s,%s,%s,%s,%s\n' % (x, y, major, minor, angle))
    logging.info("Done writing ellipses to %s" % outfile )

def get_rois( frames, window):
    global shape_
    shape_ = frames[0].shape
    activityVec = get_activity_vector( frames )
    
    images_['activity'] = np.array( activityVec )

    # activityVec contains the indices where we see a local maxima of mean
    # activity e.g. most likely here we have a activity at its peak. Now we
    # collect few frames before and after it and do the rest.
    # logger.debug("Activity vector: %s" % activityVec )
    allEdges = np.zeros( shape_ )
    roi = np.zeros( shape_ ) 
    for i in activityVec:
        low = max(0, i-window)
        high = min( shape_[0], i+window)
        bundle = frames[low:high]
        sumAll = np.zeros( shape_ )
        for f in bundle:
            e = threshold_frame( f, nstd = 2)
            sumAll += e
        edges = get_edges( sumAll )

        # merge_image = np.concatenate( (to_grayscale(sumAll), edges), axis=0)
        # save_image( 'edges_%s.png' % i, merge_image)

        #  Also creates a list of acceptable cells in each frame.
        cellImg = compute_cells( edges )

        ## save_image( 'cell_%s.png' % i, cellImg )
        roi += cellImg
        allEdges += edges 

    images_['all_edges'] = allEdges
    images_['rois'] = to_grayscale(roi)

    # save_image( 'all_edges.png', allEdges, title = 'All edges')
    # save_image( 'rois.png', roi )

    #  Use this to locate the clusters of cell in all frames. 
    cnts, cntImgs = find_contours( to_grayscale(roi), draw = True, fill = True)
    images_['bound_area'] = get_edges( cntImgs )

def find_contours( img, **kwargs ):
    logger.debug("find_contours with option: %s" % kwargs)
    # Just return external points of contours, and apply Ten-Chin chain
    # approximation algorithm. 
    
    contours, h = cv2.findContours(img
            , cv2.RETR_LIST              # No Homo Hierarichus!
            , cv2.CHAIN_APPROX_TC89_KCOS # Apply Tin-Chen algo to return
                                         # dominant point of curve.
            )
    if kwargs.get('hull', True):
        logger.debug("Approximating contours with hull")
        contours = [ cv2.convexHull( x ) for x in contours ]

    if kwargs.get('filter', 0):
        contours = filter(lambda x:len(x) >= kwargs['filter'], contours)

    contourImg = None
    if kwargs.get('draw', False):
        contourImg = np.zeros( img.shape, dtype=np.uint8 )
        cv2.drawContours( contourImg, contours, -1, 255, 1)

    if kwargs.get('fill', False):
        for c in contours:
            cv2.fillConvexPoly( contourImg, c, 255 )
    return contours, contourImg

def acceptable( contour ):
    """Various conditions under which a contour is not a cell """
    global cells_
    # First fit it with an ellipse
    cell = Cell( contour )
    if cell.area < config.min_neuron_area:
        logger.debug("Rejected contour because cell area was too low")
        return False

    if cell.area > config.max_neuron_area:
        logger.debug(
                "Rejected contour %s because of its area=%s" % (contour, cell.area)
            )
        return False

    # If the lower axis is 0.7 or more times of major axis, then aceept it.
    if cell.eccentricity < 0.7:
        msg = "Contour %s is rejected because " % contour
        msg += "axis ration (%s) of cell is too skewed" % cell.eccentricity
        logger.debug( msg )
        return False

    cells_.append( cell )
    return True

def compute_cells( image ):
    thresholdImg = threshold_frame( image, nstd = 3 )
    contourThres = config.min_points_in_contours
    contours, contourImg = find_contours(thresholdImg
            , draw = True
            , filter = contourThres
            , hull = True
            )

    img = np.zeros( contourImg.shape, dtype = np.uint8 )
    for c in contours:
        if acceptable( c ):
            cv2.fillConvexPoly( img, c, 255)

    # Now fetch the contours from this image. 
    contours, contourImg = find_contours( img, draw = True, hull = True )
    return contourImg

def df_by_f( roi, frames ):
    logger.info( "ROI: %s" % str(roi) )
    yvec = []
    for f in frames:
        col, row, w, h = roi
        area = f[row:row+h,col:col+w]
        yvec.append( area.mean() )

    yvec = np.array(yvec, dtype=np.float)
    df = yvec - yvec.min()
    return np.divide(100 * df, yvec) 

def df_by_f_data( rois, frames ):
    global save_direc_

    dfmat = np.zeros( shape = ( len(rois), len(frames) ))
    for i, r in enumerate(rois):
        vec = df_by_f( r, frames )
        dfmat[i,:] = vec
    
    outfile = '%s/df_by_f.dat' % save_direc_
    comment = 'Each column represents a ROI'
    comment += "\ni'th row is the values of ROIs in image senquence i"
    # np.savetxt(outfile, dfmat.T, delimiter=',', header = comment)
    # save_image( 'df_by_f.png', dfmat)
    # logger.info('Wrote df/f data to %s' % outfile)
    return dfmat

def merge_or_reject_cells( cells ):
    restult = []
    coolcells, areas = [], []

    # sort according to area
    cells = sorted( cells, key = lambda x: x.area )

    # Get cells with with area in sweat range : 10 - 12 um diameter.
    # keypoins = [ cv2.KeyPoint(c.center[0], c.center[1], c.radius ) for c in cells ]
    cells = helper.remove_duplicates( cells )

    # Now remove all those cells which are inside another cells. They should be
    # close enough in size.
    cells = helper.remove_contained_cells( cells )
    return cells

def get_roi_containing_minimum_cells( ):
    global images_
    global shape_

    neuronImg = np.zeros( shape = shape_ )
    coolcells = []
    for cell in cells_:
        # If area of contour is too low, reject it.
        area = cell.area
        if area < config.min_neuron_area:
            continue
        coolcells.append( cell )

    # Now we need reject some of these rectangles.
    coolerCells = merge_or_reject_cells( coolcells )

    # Replace boxex with cells later.
    boxes = []
    for c in coolerCells:
        (x, y), r = c.circle
        cr = cv2.circle( neuronImg, (int(x), int(y)), int(r) , 255, 1)
        boxes.append( c.rectangle )
    images_['neurons'] = neuronImg
    return set(boxes)

def process_tiff_file( tiff_file, bbox = None ):
    global save_direc_
    global images_

    logger.info("Processing %s" % tiff_file)
    tiff = Image.open( tiff_file )
    frames = []
    try:
        i = 0
        while 1:
            i += 1
            tiff.seek( tiff.tell() + 1 )
            framedata = get_frame_data( tiff )
            if bbox:
                framedata = framedata[bbox[0]:bbox[2], bbox[1]:bbox[3]]
            frames.append( framedata )
    except EOFError as e:
        logger.info("Total frames: %s" % i )
        logger.info("All frames are processed")

    # get the summary of all activity
    summary = np.zeros( shape = frames[0].shape )
    for f in frames: summary += f
    images_['summary'] = to_grayscale( summary )

    get_rois( frames, window = config.n_frames)

    # Here we use the collected rois which are acceptable as cells and filter
    # out overlapping contours
    boxes = get_roi_containing_minimum_cells( )

    dfmat = df_by_f_data( boxes, frames )
    images_['df_by_f'] = dfmat

def plot_results( ):
    global images_

    ax = plt.subplot(3, 2, 1)
    ax.imshow( images_['summary'] )
    ax.set_title( "Summary of activity in region", fontsize = 10 )

    ax = plt.subplot(3, 2, 2)
    ax.imshow(  images_['rois'] )
    ax.set_title( 'Computed ROIs', fontsize = 10 )

    ax = plt.subplot(3, 2, 3)
    ax.imshow( 0.99*images_['summary'] + images_['bound_area'] )
    ax.set_title( 'Clusters for df/F', fontsize = 10 )

    ax = plt.subplot(3, 2, 4)
    ax.imshow( images_['neurons'] )
    ax.set_title('Maximal set of ROIs', fontsize = 10)

    ax = plt.subplot( 3, 1, 3, frameon=False ) 
    im = ax.imshow( images_['df_by_f'] )
    ax.set_title( '100*df/F in rectangle(cluster). Baseline, min() of vector' 
            , fontsize = 10
            )
    plt.colorbar( im, orientation = 'horizontal' )

    stamp = datetime.datetime.now().isoformat()

    txt = "%s" % config.args_.file.split('/')[-1]
    txt += ' @ %s' % stamp
    txt += ', 1 px = %s micro-meter' % config.args_.pixal_size
    plt.suptitle(txt
            , fontsize = 8
            , horizontalalignment = 'left'
            , verticalalignment = 'bottom' 
            )
    plt.tight_layout( 1.5 )
    logger.info('Saved results to %s' % config.args_.outfile)
    plt.savefig( config.args_.outfile )

def get_bounding_box( ):
    bbox = [ int(x) for x in config.args_.box.split(',') ]
    r1, c1, h, w = bbox

    if h == -1: r2 = h
    else: r2 = r1 + h
    if w == -1: c2 = w
    else: c2 = c1 + w
    return (r1, c1, r2, c2)

def main( ):
    init( )
    tiffFile = config.args_.file
    bbox = get_bounding_box( )
    logger.info("== Bounding box: %s" % str(bbox))
    process_tiff_file( tiffFile, bbox = bbox )
    plot_results( )

if __name__ == '__main__':
    import argparse
    # Argument parser.
    description = '''What it does? README.md file or Ask dilawars@ncbs.res.in'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--file', '-f'
        , required = True
        , help = 'path to tiff file.'
        )
    parser.add_argument('--box', '-b'
        , required = False
        , default = "0,0,-1,-1"
        , help = 'Bounding box  row1,column1,row2,column2 e.g 0,0,100,100'
        )
    parser.add_argument('--outfile', '-o'
        , required = False
        , default = ""
        , type = str
        , help = 'result file (image)' 
        )
    parser.add_argument('--pixal_size', '-px'
        , required = True
        , type = float
        , help = 'Pixal size in micro meter'
        )

    parser.parse_args(namespace=config.args_)
    config.args_.outfile = config.args_.outfile or ('%s_out.png' % config.args_.file)
    main()
