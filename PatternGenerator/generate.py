#!/usr/bin/env python3
# -*- coding: utf-8 -*-
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import numpy as np
import pathlib
import random
import cv2
import datetime

def show_img(img, outfile, delay=10):
    img = img.T
    cv2.imshow("Pattern", img)
    print(f"-> Saving to {outfile}")
    cv2.imwrite('%s'%outfile, img)
    cv2.waitKey(delay)

def detectTrial(imgdir):
    subdirs = [x.name for x in imgdir.iterdir() if x.is_dir()]
    trials = [int(str(x).replace('Trial', '')) for x in subdirs if 'Trial' in str(x)]
    print(trials)
    if not trials:
        trials = [0]
    newTrial = "Trial%04d" % (1+max(trials))
    return imgdir / newTrial

def main(**kwargs):
    basedir = pathlib.Path(str(datetime.datetime.now().date()))
    basedir.mkdir(parents=True, exist_ok=True)
    imgdir = detectTrial(basedir)
    imgdir.mkdir(parents=True, exist_ok=True)
    print( f"[INFO ] Saving to {imgdir}" )

    kwargs['imgdir'] = imgdir
    random.seed(kwargs.get('seed', 2019))
    imgs = []
    for i in range(kwargs['num_patterns']):
        img = generate_pattern(i, **kwargs)
        imgs.append(img)

    # get the mean and save.
    sumI = np.sum(imgs, axis=0) 
    avgI = np.mean(imgs, axis=0)
    avgI = avgI - avgI.min()
    avgI = 255*avgI//avgI.max()
    cv2.imwrite( "average.png", np.hstack((sumI,avgI)))

def generate_pattern(i, **kwargs):
    shape = [int(x) for x in kwargs['ROI'].split('x')]
    nRect = int(kwargs['num_rect']) 
    rectSize = [int(x) for x in
    kwargs['size_pattern'].split('x')] 
    dx, dy = rectSize[0]//2, rectSize[1]//2
    xs = random.sample(range(rectSize[0], shape[0]-rectSize[0], rectSize[0]), nRect) 
    ys = random.sample(range(rectSize[1], shape[1]-rectSize[1], rectSize[1]), nRect) 
    img = np.zeros(shape=shape, dtype=np.uint8) # add rectangles.
    for x, y in zip(xs, ys):
        cv2.rectangle(img, (y-dy,x-dx), (y+dy, x+dy), 255, -1)
    show_img(img, kwargs['imgdir']/f'{i:05d}.png')
    return img


if __name__ == '__main__':
    import argparse
    # Argument parser.
    description = '''Generate PNG file for projector.'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--ROI', '-r'
        , required = False, default='684x608'
        , help = 'Size of ROI in pixels.'
        )
    parser.add_argument('--num-patterns', '-np'
        , required = False, default=100, type=int
        , help = 'Number of patterns to generate.'
        )
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--num-rect', '-nr'
        , required=False, default=50, type=int
        , help = 'Number of rectangles to put on an image.'
        )
    g.add_argument('--loc', '-l'
        , required=False, type=str
        , help = 'location of rectangles e.g., x1:y1,x2:y2 etc.'
        )
    parser.add_argument('--size-pattern', '-sp'
        , required = False, default='8x8', type=str
        , help = 'Size of each rectangle.'
        )
    parser.add_argument('--noise', '-n'
        , required = False, default=0.0, type=float
        , help = 'Gaussian noise (std) in each rectangle location.'
                 'Only when position of each rectangle is given'
        )
    parser.add_argument('--seed', '-s'
        , required = False, type=int, default=2019
        , help = 'random seed.'
        )
    class Args: pass 
    args = Args()
    parser.parse_args(namespace=args)
    main(**vars(args))
