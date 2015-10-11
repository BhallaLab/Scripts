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

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    filename='default.log',
    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
_logger = logging.getLogger('blinky')
_logger.addHandler(console)

max_length_ = 80
current_length_ = 0
frame_no_ = 1
avg_img_ = None

def process_frame(frame, **kwargs):
    # Find edge in frame
    global avg_img_, frame_no_
    new = np.copy(frame)
    return frame, avg_img_, None

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
    global avg_img_, frame_no_
    cap = cv2.VideoCapture(video_file_name)
    totalFrames = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    _logger.info("Total frames: %s" % totalFrames)
    fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
    _logger.info("| FPS: %s" % fps)
    vec = []
    tvec = []
    avg_img_ = cv2.cvtColor(cap.read()[1], cv2.COLOR_RGB2GRAY)
    while(cap.isOpened()):
        ret, frame = cap.read()
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        except Exception as e:
            _logger.warn("can't convert frame %s to grayscale. Done" % frame_no_)
            print(e)
            break
        nRows, nCols = gray.shape
        if args.get('bbox'):
            x0, y0, w, h = args['bbox']
            gray = gray[y0:y0+h,x0:x0+w]
        try:
            infile, outfile, res = process_frame(gray)
        except Exception as e:
            _logger.warn("Failed to process frame %s. Stopping .." % frame_no_)
            print(e)
            break
        frame_no_ += 1
        tvec.append(frame_no_*1.0/float(fps))
        vec.append(res)
        result = np.concatenate((infile, outfile), axis=1)
        cv2.imshow('Eye-Blink', result)
        if wait_for_exit_key():
            break
    cv2.destroyAllWindows()
    outfile = "%s_out.csv" % (video_file_name)
    _logger.info("Writing to %s" % outfile)
    np.savetxt(outfile, np.array((tvec, vec)).T, delimiter=",", header = "time,area")

def main(args):
    fileName = args['video_file']
    process_video(fileName, args = args)

if __name__ == '__main__':
    import argparse
    # Argument parser.
    description = '''description'''
    parser = argparse.ArgumentParser(description=description)
    class Args: pass 
    args = Args()
    parser.add_argument('--video-file', '-f'
        , required = True
        , help = 'Path of the video file'
        )
    parser.add_argument('--bbox', '-b'
        , required = False
        , nargs = '+'
        , type = int
        , help = 'Bounding box : topx topy width height'
        )
    parser.parse_args(namespace=args)
    main(vars(args))

