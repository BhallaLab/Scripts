#!/usr/bin/env python

"""blinky.py: 

Starting point of blinky

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2015, Dilawar Singh and NCBS Bangalore"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import extract
import webcam
import pylab
import numpy as np

def main(args):
    # Extract video first
    data = webcam.video2csv(args)
    result = extract.find_blinks(data)
    tBlink, wBlink = result['blinks']
    outfile = "%s_blinks.csv" % args['video_file']
    print("[INFO] Writing to outfile %s" % outfile)
    np.savetxt(outfile, np.array([tBlink, wBlink]).T
            , delimiter=","
            , header = "seconds,blink_weight"
            )

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

