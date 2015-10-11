"""
Extract a csv file out of video file representing eye blinks.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2015, Dilawar Singh and NCBS Bangalore"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import cv2
import numpy as np
import sys
import time
import pylab
import logging
import datetime

_logger = logging.getLogger('blinky')

max_length_ = 80
current_length_ = 0

def get_ellipse(cnts):
    ellipses = []
    for cnt in cnts[0]:
        try:
            e = cv2.fitEllipse(cnt)
            ellipses.append(e)
        except: pass
    return ellipses

def merge_contours(cnts, img):
    """Merge these contours together. And create an image"""
    for c in cnts:
        hull = cv2.convexHull(c)
        cv2.fillConvexPoly(img, hull, 0)
    return img

def draw_stars(current, max_lim):
    """Draw starts onto console as progress bar. Only if there is any change in
    length.
    """
    global current_length_, max_length_
    stride = int( max_lim / float(max_length_)) 
    steps = int(current / float(stride))
    if steps == current_length_:
        return
    current_length_ = steps
    msg = "".join([ '*' for x in range(steps) ] + 
            ['|' for x in range(max_length_-steps)]
            )
    print(msg)

def process_frame(frame):
    # Find edge in frame
    edges = cv2.Canny(frame, 50, 250)
    cnts = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cntImg = np.ones(frame.shape)
    merge_contours(cnts[0], cntImg)

    # cool, find the contour again and convert again. Sum up their area.
    im = np.array((1-cntImg) * 255, dtype = np.uint8)
    cnts = cv2.findContours(im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    hullImg = np.ones(frame.shape)
    res = []
    for c in cnts[0]:
        c = cv2.convexHull(c)
        cv2.fillConvexPoly(hullImg, c, 0, 8)
        res.append(cv2.contourArea(c))

    hullImg = np.array((1-hullImg) * 255, dtype = np.uint8)
    return frame, hullImg, sum(res)

def wait_for_exit_key():
    # This continue till one presses q.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return True
    return False
    #k = cv2.waitKey(0)
    #if k==27:    # Esc key to stop
    #    break
    #elif k==-1:  # normally -1 returned,so don't print it
    #    continue
    #else:
    #    print k # else print its value

def process_video(video_file_name,  args = {}):
    cap = cv2.VideoCapture(video_file_name)
    totalFrames = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    _logger.info("Total frames: %s" % totalFrames)
    fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
    _logger.info("| FPS: %s" % fps)
    vec = []
    tvec = []
    nFrames = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        except Exception as e:
            _logger.warn("can't convert frame %s to grayscale. Done" % nFrames)
            print(e)
            break
        nRows, nCols = gray.shape
        if args.get('bbox'):
            x0, y0, w, h = args['bbox']
            gray = gray[y0:y0+h,x0:x0+w]
        try:
            infile, outfile, res = process_frame(gray)
        except Exception as e:
            _logger.warn("Failed to process frame %s. Stopping .." % nFrames)
            print(e)
            break
        nFrames += 1.0
        draw_stars(nFrames, totalFrames)
        tvec.append(nFrames*1.0/fps)
        vec.append(res)
        result = np.concatenate((infile, outfile), axis=1)
        cv2.imshow('Eye-Blink', result)
        if wait_for_exit_key():
            break
    cv2.destroyAllWindows()
    outfile = "%s_out.csv" % (video_file_name)
    _logger.info("Writing to %s" % outfile)
    data = np.array((tvec, vec)).T
    np.savetxt(outfile, data, delimiter=",", header = "time,area")
    return data

def video2csv(args):
    fileName = args['video_file']
    return process_video(fileName, args = args)
